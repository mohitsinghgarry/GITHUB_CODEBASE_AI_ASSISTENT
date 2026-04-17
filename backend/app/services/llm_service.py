"""
LLM Service for Ollama integration.

This module provides a wrapper around the Ollama HTTP API for local LLM inference.
It handles connection management, timeout handling, retry logic with exponential backoff,
and system prompt configuration for different explanation modes.

Requirements:
- 9.1: Connect to configured Ollama instance
- 9.2: Return error if Ollama is unavailable
- 9.3: Support configurable model selection
- 9.4: Include system instructions for code-focused responses
- 9.5: Handle timeouts and retry with exponential backoff
- 9.6: Log errors and return user-friendly messages
- 9.7: Support streaming responses
- 9.8: Provide endpoint to list available models
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


# ============================================================================
# Explanation Modes (Requirement 9.4)
# ============================================================================


class ExplanationMode(str, Enum):
    """
    Explanation modes for different user preferences.
    
    Each mode configures the system prompt to tailor the LLM's response style.
    """
    BEGINNER = "beginner"
    TECHNICAL = "technical"
    INTERVIEW = "interview"


# System prompts for each explanation mode
SYSTEM_PROMPTS = {
    ExplanationMode.BEGINNER: (
        "You are a helpful coding tutor. Explain concepts clearly with examples. "
        "Avoid jargon and use simple language. When explaining code, break it down "
        "step by step. Use analogies when helpful. Always be encouraging and patient. "
        "\n\nWhen explaining code, follow this format:\n"
        "1. First, show the COMPLETE code in a single code block with language tag (```javascript, ```python, etc.)\n"
        "2. Then add a heading '## Line-by-Line Explanation' or '🔍 Line-by-Line Explanation'\n"
        "3. For each line, show the line in a small code block, then explain with bullet points\n"
        "Example:\n"
        "```javascript\n"
        "function example() {\n"
        "  return 42;\n"
        "}\n"
        "```\n\n"
        "## Line-by-Line Explanation\n\n"
        "### Line 1\n"
        "```javascript\n"
        "function example() {\n"
        "```\n"
        "- Defines a function named `example`\n"
        "- Takes no parameters\n"
    ),
    ExplanationMode.TECHNICAL: (
        "You are an expert software engineer. Provide concise, precise technical answers. "
        "Focus on the key points without unnecessary elaboration. Be direct and to the point. "
        "\n\nWhen explaining code, follow this EXACT format:\n"
        "1. First, show the COMPLETE code in a single code block with language tag (```javascript, ```python, etc.)\n"
        "2. Then add a heading '## Line-by-Line Explanation' or '🔍 Line-by-Line Explanation'\n"
        "3. For each important line or section:\n"
        "   - Add a subheading like '### Line 1' or '🔹 Line 1'\n"
        "   - Show that specific line in a code block\n"
        "   - Explain with bullet points\n"
        "\nExample format:\n"
        "```javascript\n"
        "const result = await api.fetch();\n"
        "```\n\n"
        "## Line-by-Line Explanation\n\n"
        "### Line 1\n"
        "```javascript\n"
        "const result = await api.fetch();\n"
        "```\n"
        "- `const result` - declares a constant variable\n"
        "- `await` - waits for the promise to resolve\n"
        "- `api.fetch()` - calls the fetch method\n"
        "\nNEVER put inline code snippets in separate blocks within lists. Use inline backticks like `variableName` for references."
    ),
    ExplanationMode.INTERVIEW: (
        "You are a technical interviewer. Ask follow-up questions to assess understanding. "
        "Explain trade-offs between different approaches. Discuss time and space complexity. "
        "Encourage the user to think critically about their solutions. Provide hints rather "
        "than direct answers when appropriate. "
        "\n\nWhen showing code examples, follow this format:\n"
        "1. Show complete code first in a code block with language tag\n"
        "2. Then break down key sections line-by-line with explanations\n"
        "3. Ask follow-up questions about specific lines or concepts\n"
    ),
}


# ============================================================================
# Request/Response Models
# ============================================================================


class OllamaGenerateRequest(BaseModel):
    """Request model for Ollama generate endpoint."""
    
    model: str = Field(..., description="Model name to use for generation")
    prompt: str = Field(..., description="The prompt to send to the model")
    system: Optional[str] = Field(None, description="System prompt for context")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Whether to stream the response")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional model options")


class OllamaGenerateResponse(BaseModel):
    """Response model for Ollama generate endpoint."""
    
    model: str = Field(..., description="Model used for generation")
    response: str = Field(..., description="Generated text")
    done: bool = Field(..., description="Whether generation is complete")
    context: Optional[List[int]] = Field(None, description="Context for continuation")
    total_duration: Optional[int] = Field(None, description="Total duration in nanoseconds")
    load_duration: Optional[int] = Field(None, description="Model load duration in nanoseconds")
    prompt_eval_count: Optional[int] = Field(None, description="Number of tokens in prompt")
    eval_count: Optional[int] = Field(None, description="Number of tokens generated")
    eval_duration: Optional[int] = Field(None, description="Generation duration in nanoseconds")


class OllamaModel(BaseModel):
    """Model information from Ollama."""
    
    name: str = Field(..., description="Model name")
    modified_at: str = Field(..., description="Last modified timestamp")
    size: int = Field(..., description="Model size in bytes")
    digest: str = Field(..., description="Model digest/hash")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional model details")


class OllamaListResponse(BaseModel):
    """Response model for Ollama list models endpoint."""
    
    models: List[OllamaModel] = Field(..., description="List of available models")


# ============================================================================
# Exceptions
# ============================================================================


class OllamaError(Exception):
    """Base exception for Ollama-related errors."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when unable to connect to Ollama."""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when Ollama request times out."""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Raised when requested model is not available."""
    pass


class OllamaGenerationError(OllamaError):
    """Raised when generation fails."""
    pass


# ============================================================================
# LLM Service
# ============================================================================


class LLMService:
    """
    Service for interacting with Ollama LLM API.
    
    This service provides methods for text generation (streaming and non-streaming),
    model listing, and health checks. It includes automatic retry with exponential
    backoff for transient failures.
    
    Requirements:
    - 9.1: Connect to configured Ollama instance
    - 9.2: Return error if Ollama is unavailable
    - 9.3: Support configurable model selection
    - 9.4: Include system instructions for code-focused responses
    - 9.5: Handle timeouts and retry with exponential backoff
    - 9.6: Log errors and return user-friendly messages
    - 9.7: Support streaming responses
    - 9.8: List available models
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the LLM service.
        
        Args:
            settings: Application settings (uses global settings if not provided)
        """
        self.settings = settings or get_settings()
        self.base_url = self.settings.ollama_base_url
        self.default_model = self.settings.ollama_model
        self.timeout = self.settings.ollama_timeout
        self.max_retries = self.settings.ollama_max_retries
        
        # HTTP client with timeout configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout, connect=10.0),
            follow_redirects=True,
        )
        
        logger.info(
            f"Initialized LLM service with Ollama at {self.base_url}, "
            f"default model: {self.default_model}"
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Closed LLM service HTTP client")
    
    # ========================================================================
    # Health Check (Requirement 9.1, 9.2)
    # ========================================================================
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is available and responding.
        
        Returns:
            bool: True if Ollama is healthy, False otherwise
            
        Requirement 9.1: Connect to configured Ollama instance
        Requirement 9.2: Return error if Ollama is unavailable
        """
        try:
            response = await self.client.get("/api/tags", timeout=5.0)
            response.raise_for_status()
            logger.info("Ollama health check passed")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def ensure_available(self) -> None:
        """
        Ensure Ollama is available, raise exception if not.
        
        Raises:
            OllamaConnectionError: If Ollama is not available
            
        Requirement 9.2: Return error if Ollama is unavailable
        """
        if not await self.health_check():
            raise OllamaConnectionError(
                f"Unable to connect to Ollama at {self.base_url}. "
                "Please ensure Ollama is running and accessible."
            )
    
    # ========================================================================
    # Model Management (Requirement 9.3, 9.8)
    # ========================================================================
    
    async def list_models(self) -> List[OllamaModel]:
        """
        List all available Ollama models.
        
        Returns:
            List[OllamaModel]: List of available models
            
        Raises:
            OllamaConnectionError: If unable to connect to Ollama
            OllamaError: If request fails
            
        Requirement 9.3: Support configurable model selection
        Requirement 9.8: Provide endpoint to list available models
        """
        try:
            response = await self._retry_request(
                method="GET",
                url="/api/tags",
            )
            
            data = response.json()
            models = OllamaListResponse(**data).models
            
            logger.info(f"Listed {len(models)} available Ollama models")
            return models
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to list Ollama models: {e}")
            raise OllamaError(f"Failed to list models: {str(e)}")
    
    async def check_model_available(self, model: str) -> bool:
        """
        Check if a specific model is available.
        
        Args:
            model: Model name to check
            
        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            models = await self.list_models()
            return any(m.name == model for m in models)
        except OllamaError:
            return False
    
    # ========================================================================
    # Text Generation (Requirement 9.4, 9.5, 9.6, 9.7)
    # ========================================================================
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        explanation_mode: Optional[ExplanationMode] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using Ollama (non-streaming).
        
        Args:
            prompt: The prompt to send to the model
            model: Model name (uses default if not provided)
            system_prompt: System prompt for context (overrides explanation_mode)
            explanation_mode: Explanation mode for system prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream (must be False for this method)
            **kwargs: Additional options to pass to Ollama
            
        Returns:
            str: Generated text
            
        Raises:
            OllamaConnectionError: If unable to connect to Ollama
            OllamaTimeoutError: If request times out
            OllamaModelNotFoundError: If model is not available
            OllamaGenerationError: If generation fails
            
        Requirement 9.4: Include system instructions for code-focused responses
        Requirement 9.5: Handle timeouts and retry with exponential backoff
        Requirement 9.6: Log errors and return user-friendly messages
        """
        if stream:
            raise ValueError("Use generate_stream() for streaming responses")
        
        # Ensure Ollama is available
        await self.ensure_available()
        
        # Use default model if not provided
        model = model or self.default_model
        
        # Determine system prompt (Requirement 9.4)
        if system_prompt is None and explanation_mode is not None:
            system_prompt = SYSTEM_PROMPTS.get(explanation_mode)
        
        # Build request
        request_data = OllamaGenerateRequest(
            model=model,
            prompt=prompt,
            system=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            options=kwargs if kwargs else None,
        )
        
        logger.info(
            f"Generating text with model '{model}', "
            f"temperature={temperature}, "
            f"explanation_mode={explanation_mode}"
        )
        
        try:
            # Make request with retry (Requirement 9.5)
            response = await self._retry_request(
                method="POST",
                url="/api/generate",
                json=request_data.model_dump(exclude_none=True),
            )
            
            # Parse response
            data = response.json()
            result = OllamaGenerateResponse(**data)
            
            logger.info(
                f"Generated {result.eval_count or 0} tokens in "
                f"{(result.eval_duration or 0) / 1e9:.2f}s"
            )
            
            return result.response
            
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out: {e}")
            raise OllamaTimeoutError(
                f"Request timed out after {self.timeout} seconds. "
                "The model may be too large or the prompt too complex."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Model '{model}' not found")
                raise OllamaModelNotFoundError(
                    f"Model '{model}' is not available. "
                    "Please pull the model using 'ollama pull {model}'."
                )
            logger.error(f"Ollama generation failed: {e}")
            raise OllamaGenerationError(
                f"Generation failed: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}", exc_info=True)
            raise OllamaGenerationError(
                "An unexpected error occurred during text generation. "
                "Please try again or contact support if the issue persists."
            )
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        explanation_mode: Optional[ExplanationMode] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Generate text using Ollama with streaming.
        
        Args:
            prompt: The prompt to send to the model
            model: Model name (uses default if not provided)
            system_prompt: System prompt for context (overrides explanation_mode)
            explanation_mode: Explanation mode for system prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional options to pass to Ollama
            
        Yields:
            str: Generated text chunks
            
        Raises:
            OllamaConnectionError: If unable to connect to Ollama
            OllamaTimeoutError: If request times out
            OllamaModelNotFoundError: If model is not available
            OllamaGenerationError: If generation fails
            
        Requirement 9.7: Support streaming responses
        """
        # Ensure Ollama is available
        await self.ensure_available()
        
        # Use default model if not provided
        model = model or self.default_model
        
        # Determine system prompt (Requirement 9.4)
        if system_prompt is None and explanation_mode is not None:
            system_prompt = SYSTEM_PROMPTS.get(explanation_mode)
        
        # Build request
        request_data = OllamaGenerateRequest(
            model=model,
            prompt=prompt,
            system=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            options=kwargs if kwargs else None,
        )
        
        logger.info(
            f"Streaming generation with model '{model}', "
            f"temperature={temperature}, "
            f"explanation_mode={explanation_mode}"
        )
        
        try:
            # Make streaming request
            async with self.client.stream(
                "POST",
                "/api/generate",
                json=request_data.model_dump(exclude_none=True),
                timeout=httpx.Timeout(self.timeout, connect=10.0),
            ) as response:
                response.raise_for_status()
                
                # Stream response chunks
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        data = OllamaGenerateResponse.model_validate_json(line)
                        if data.response:
                            yield data.response
                        
                        if data.done:
                            logger.info(
                                f"Streaming complete: {data.eval_count or 0} tokens in "
                                f"{(data.eval_duration or 0) / 1e9:.2f}s"
                            )
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse streaming chunk: {e}")
                        continue
                        
        except httpx.TimeoutException as e:
            logger.error(f"Ollama streaming request timed out: {e}")
            raise OllamaTimeoutError(
                f"Streaming request timed out after {self.timeout} seconds."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Model '{model}' not found")
                raise OllamaModelNotFoundError(
                    f"Model '{model}' is not available. "
                    "Please pull the model using 'ollama pull {model}'."
                )
            logger.error(f"Ollama streaming generation failed: {e}")
            raise OllamaGenerationError(
                f"Streaming generation failed: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {e}", exc_info=True)
            raise OllamaGenerationError(
                "An unexpected error occurred during streaming generation."
            )
    
    # ========================================================================
    # Retry Logic with Exponential Backoff (Requirement 9.5)
    # ========================================================================
    
    async def _retry_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments to pass to httpx
            
        Returns:
            httpx.Response: HTTP response
            
        Raises:
            httpx.HTTPError: If all retries are exhausted
            
        Requirement 9.5: Handle timeouts and retry with exponential backoff
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
                
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    # Calculate exponential backoff delay
                    delay = min(2 ** attempt, 30)  # Cap at 30 seconds
                    
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay}s..."
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Request failed after {self.max_retries + 1} attempts: {e}"
                    )
                    
            except httpx.HTTPStatusError as e:
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    raise
                
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = min(2 ** attempt, 30)
                    
                    logger.warning(
                        f"Request failed with status {e.response.status_code} "
                        f"(attempt {attempt + 1}/{self.max_retries + 1}). "
                        f"Retrying in {delay}s..."
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Request failed after {self.max_retries + 1} attempts: {e}"
                    )
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        
        raise OllamaError("Request failed for unknown reason")
    
    # ========================================================================
    # Convenience Methods
    # ========================================================================
    
    async def generate_with_mode(
        self,
        prompt: str,
        explanation_mode: ExplanationMode = ExplanationMode.TECHNICAL,
        **kwargs: Any,
    ) -> str:
        """
        Generate text with a specific explanation mode.
        
        Args:
            prompt: The prompt to send to the model
            explanation_mode: Explanation mode for system prompt
            **kwargs: Additional arguments to pass to generate()
            
        Returns:
            str: Generated text
        """
        return await self.generate(
            prompt=prompt,
            explanation_mode=explanation_mode,
            **kwargs,
        )
    
    async def generate_code_explanation(
        self,
        code: str,
        question: str,
        explanation_mode: ExplanationMode = ExplanationMode.TECHNICAL,
        **kwargs: Any,
    ) -> str:
        """
        Generate an explanation for code.
        
        Args:
            code: The code to explain
            question: The question about the code
            explanation_mode: Explanation mode for system prompt
            **kwargs: Additional arguments to pass to generate()
            
        Returns:
            str: Generated explanation
        """
        prompt = f"""Here is some code:

```
{code}
```

Question: {question}

Please provide a clear explanation."""
        
        return await self.generate(
            prompt=prompt,
            explanation_mode=explanation_mode,
            **kwargs,
        )


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_llm_service() -> LLMService:
    """
    Dependency injection for LLM service.
    
    Returns:
        LLMService: Initialized LLM service instance
    """
    service = LLMService()
    try:
        yield service
    finally:
        await service.close()

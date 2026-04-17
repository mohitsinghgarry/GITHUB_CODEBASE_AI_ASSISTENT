"""
Groq LLM Service for fast cloud-based inference.

This module provides a wrapper around the Groq API for ultra-fast LLM inference.
Groq provides blazing-fast inference speeds (up to 500+ tokens/second).

Usage:
    1. Get API key from https://console.groq.com/
    2. Set GROQ_API_KEY in environment variables
    3. Set LLM_PROVIDER=groq in .env
"""

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Optional

import httpx
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.llm_service import (
    ExplanationMode,
    SYSTEM_PROMPTS,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelNotFoundError,
    OllamaGenerationError,
    OllamaError,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Groq Models
# ============================================================================

GROQ_MODELS = {
    # OpenAI Open Models (NEW!)
    "openai/gpt-oss-120b": "OpenAI GPT-OSS 120B - Flagship open model with reasoning capabilities",
    "openai/gpt-oss-20b": "OpenAI GPT-OSS 20B - Ultra fast, cost-effective",
    
    # Fast models (recommended for chat)
    "llama-3.3-70b-versatile": "Meta Llama 3.3 70B - Best balance of speed and quality",
    "llama-3.1-8b-instant": "Meta Llama 3.1 8B - Ultra fast, good for simple queries",
    "mixtral-8x7b-32768": "Mixtral 8x7B - Great for code, 32K context",
    
    # Specialized models
    "llama-3.1-70b-versatile": "Meta Llama 3.1 70B - High quality responses",
    "gemma2-9b-it": "Google Gemma 2 9B - Efficient and capable",
}

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


# ============================================================================
# Request/Response Models
# ============================================================================


class GroqMessage(BaseModel):
    """Message in Groq chat format."""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")


class GroqChatRequest(BaseModel):
    """Request model for Groq chat endpoint."""
    model: str = Field(..., description="Model name")
    messages: list[GroqMessage] = Field(..., description="Chat messages")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Max tokens to generate")
    stream: bool = Field(False, description="Whether to stream")
    top_p: float = Field(1.0, ge=0.0, le=1.0)


class GroqUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class GroqChoice(BaseModel):
    """Response choice."""
    index: int
    message: GroqMessage
    finish_reason: str


class GroqChatResponse(BaseModel):
    """Response model for Groq chat endpoint."""
    id: str
    object: str
    created: int
    model: str
    choices: list[GroqChoice]
    usage: GroqUsage


# ============================================================================
# Groq LLM Service
# ============================================================================


class GroqLLMService:
    """
    Service for interacting with Groq API.
    
    Provides ultra-fast LLM inference with the same interface as OllamaLLMService.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        settings: Optional[Settings] = None
    ):
        """
        Initialize the Groq LLM service.
        
        Args:
            api_key: Groq API key (reads from env if not provided)
            model: Default model to use
            settings: Application settings
        """
        self.settings = settings or get_settings()
        
        # Get API key from parameter or environment
        import os
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Get your API key from https://console.groq.com/"
            )
        
        # Set default model
        self.default_model = model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        
        # Groq API endpoint
        self.base_url = "https://api.groq.com/openai/v1"
        
        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(60.0, connect=10.0),
        )
        
        logger.info(
            f"Initialized Groq LLM service with model: {self.default_model}"
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Closed Groq LLM service HTTP client")
    
    # ========================================================================
    # Health Check
    # ========================================================================
    
    async def health_check(self) -> bool:
        """
        Check if Groq API is available.
        
        Returns:
            bool: True if Groq is healthy, False otherwise
        """
        try:
            # Try a simple completion to verify API key and connectivity
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.default_model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                },
                timeout=5.0,
            )
            response.raise_for_status()
            logger.info("Groq health check passed")
            return True
        except httpx.HTTPError as e:
            logger.error(f"Groq health check failed: {e}")
            return False
    
    async def ensure_available(self) -> None:
        """
        Ensure Groq is available, raise exception if not.
        
        Raises:
            OllamaConnectionError: If Groq is not available
        """
        if not await self.health_check():
            raise OllamaConnectionError(
                "Unable to connect to Groq API. "
                "Please check your API key and internet connection."
            )
    
    # ========================================================================
    # Model Management
    # ========================================================================
    
    async def list_models(self) -> list[str]:
        """
        List available Groq models.
        
        Returns:
            list[str]: List of available model names
        """
        return list(GROQ_MODELS.keys())
    
    async def check_model_available(self, model: str) -> bool:
        """
        Check if a specific model is available.
        
        Args:
            model: Model name to check
            
        Returns:
            bool: True if model is available
        """
        return model in GROQ_MODELS
    
    # ========================================================================
    # Text Generation
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
        Generate text using Groq (non-streaming).
        
        Args:
            prompt: The prompt to send to the model
            model: Model name (uses default if not provided)
            system_prompt: System prompt for context
            explanation_mode: Explanation mode for system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream (must be False for this method)
            **kwargs: Additional options
            
        Returns:
            str: Generated text
        """
        if stream:
            raise ValueError("Use generate_stream() for streaming responses")
        
        # Use default model if not provided
        model = model or self.default_model
        
        # Determine system prompt
        if system_prompt is None and explanation_mode is not None:
            system_prompt = SYSTEM_PROMPTS.get(explanation_mode)
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append(GroqMessage(role="system", content=system_prompt))
        messages.append(GroqMessage(role="user", content=prompt))
        
        # Build request
        request_data = GroqChatRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or 2048,
            stream=False,
        )
        
        logger.info(
            f"Generating text with Groq model '{model}', "
            f"temperature={temperature}"
        )
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json=request_data.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            result = GroqChatResponse(**data)
            
            logger.info(
                f"Generated {result.usage.completion_tokens} tokens "
                f"(total: {result.usage.total_tokens})"
            )
            
            return result.choices[0].message.content
            
        except httpx.TimeoutException as e:
            logger.error(f"Groq request timed out: {e}")
            raise OllamaTimeoutError("Request timed out")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.error(f"Model '{model}' not found")
                raise OllamaModelNotFoundError(f"Model '{model}' not available")
            elif e.response.status_code == 401:
                logger.error("Invalid Groq API key")
                raise OllamaConnectionError("Invalid API key")
            logger.error(f"Groq generation failed: {e}")
            raise OllamaGenerationError(f"Generation failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise OllamaGenerationError(str(e))
    
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
        Generate text using Groq with streaming.
        
        Args:
            prompt: The prompt to send to the model
            model: Model name
            system_prompt: System prompt for context
            explanation_mode: Explanation mode
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional options
            
        Yields:
            str: Generated text chunks
        """
        # Use default model if not provided
        model = model or self.default_model
        
        # Determine system prompt
        if system_prompt is None and explanation_mode is not None:
            system_prompt = SYSTEM_PROMPTS.get(explanation_mode)
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Build request
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 2048,
            "stream": True,
        }
        
        logger.info(f"Streaming generation with Groq model '{model}'")
        
        try:
            async with self.client.stream(
                "POST",
                "/chat/completions",
                json=request_data,
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip() or line.strip() == "data: [DONE]":
                        continue
                    
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                        
        except httpx.TimeoutException as e:
            logger.error(f"Groq streaming timed out: {e}")
            raise OllamaTimeoutError("Streaming request timed out")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise OllamaConnectionError("Invalid API key")
            logger.error(f"Groq streaming failed: {e}")
            raise OllamaGenerationError(f"Streaming failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {e}", exc_info=True)
            raise OllamaGenerationError(str(e))
    
    # ========================================================================
    # Convenience Methods
    # ========================================================================
    
    async def generate_with_mode(
        self,
        prompt: str,
        explanation_mode: ExplanationMode = ExplanationMode.TECHNICAL,
        **kwargs: Any,
    ) -> str:
        """Generate text with a specific explanation mode."""
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
        """Generate an explanation for code."""
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
# Factory Function
# ============================================================================


def create_llm_service(provider: Optional[str] = None) -> Any:
    """
    Create an LLM service based on provider.
    
    Args:
        provider: "ollama" or "groq" (reads from LLM_PROVIDER env var if not provided)
        
    Returns:
        LLM service instance
    """
    import os
    
    # Read from environment variable if not provided
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "ollama")
    
    provider = provider.lower()
    
    logger.info(f"Creating LLM service with provider: {provider}")
    
    if provider == "groq":
        return GroqLLMService()
    else:
        from app.services.llm_service import LLMService
        return LLMService()

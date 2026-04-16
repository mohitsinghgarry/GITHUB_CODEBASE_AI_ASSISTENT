# LLM Service Implementation

## Overview

The LLM Service provides a comprehensive wrapper around the Ollama HTTP API for local LLM inference. It handles connection management, timeout handling, retry logic with exponential backoff, and system prompt configuration for different explanation modes.

## Features Implemented

### 1. Connection Management (Requirement 9.1, 9.2)
- Async HTTP client with configurable timeout
- Health check endpoint to verify Ollama availability
- `ensure_available()` method that raises exception if Ollama is not accessible
- Automatic connection pooling via httpx

### 2. Model Management (Requirement 9.3, 9.8)
- `list_models()` - List all available Ollama models
- `check_model_available()` - Check if a specific model exists
- Support for configurable model selection
- Default model configuration via settings

### 3. Text Generation (Requirement 9.4, 9.6, 9.7)
- **Non-streaming generation**: `generate()` method
- **Streaming generation**: `generate_stream()` method
- Configurable temperature, max_tokens, and other parameters
- Support for custom system prompts
- Comprehensive error handling with user-friendly messages

### 4. Explanation Modes (Requirement 9.4)
Three built-in explanation modes with tailored system prompts:
- **Beginner**: Simple explanations with examples, avoiding jargon
- **Technical**: Detailed technical explanations with best practices
- **Interview**: Interactive style with follow-up questions and trade-offs

### 5. Retry Logic with Exponential Backoff (Requirement 9.5)
- Automatic retry on transient failures (timeouts, connection errors)
- Exponential backoff: 1s, 2s, 4s, 8s, etc. (capped at 30s)
- Configurable max retries (default: 3)
- No retry on 4xx client errors
- Detailed logging of retry attempts

### 6. Error Handling (Requirement 9.6)
Custom exception hierarchy:
- `OllamaError` - Base exception
- `OllamaConnectionError` - Connection failures
- `OllamaTimeoutError` - Request timeouts
- `OllamaModelNotFoundError` - Model not available
- `OllamaGenerationError` - Generation failures

All errors include user-friendly messages and detailed logging.

## API Reference

### Initialization

```python
from app.services.llm_service import LLMService

# Use default settings
service = LLMService()

# Use custom settings
from app.core.config import Settings
settings = Settings(ollama_base_url="http://custom:11434")
service = LLMService(settings=settings)
```

### Health Check

```python
# Check if Ollama is available
is_healthy = await service.health_check()

# Ensure Ollama is available (raises exception if not)
await service.ensure_available()
```

### List Models

```python
# Get all available models
models = await service.list_models()
for model in models:
    print(f"{model.name}: {model.size / (1024**3):.2f} GB")

# Check if specific model exists
exists = await service.check_model_available("codellama:7b")
```

### Text Generation (Non-Streaming)

```python
# Basic generation
response = await service.generate(
    prompt="Explain Python decorators",
    temperature=0.7,
)

# With explanation mode
response = await service.generate(
    prompt="What is a closure?",
    explanation_mode=ExplanationMode.BEGINNER,
)

# With custom system prompt
response = await service.generate(
    prompt="Explain async/await",
    system_prompt="You are a Python expert. Be concise.",
    temperature=0.5,
    max_tokens=200,
)

# With custom model
response = await service.generate(
    prompt="Review this code",
    model="deepseek-coder:6.7b",
)
```

### Text Generation (Streaming)

```python
# Stream response chunks
async for chunk in service.generate_stream(
    prompt="Write a Python function to sort a list",
    explanation_mode=ExplanationMode.TECHNICAL,
):
    print(chunk, end="", flush=True)
```

### Convenience Methods

```python
# Generate with specific mode
response = await service.generate_with_mode(
    prompt="Explain recursion",
    explanation_mode=ExplanationMode.INTERVIEW,
)

# Generate code explanation
response = await service.generate_code_explanation(
    code="def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    question="How does this work?",
    explanation_mode=ExplanationMode.BEGINNER,
)
```

### Cleanup

```python
# Close the HTTP client
await service.close()

# Or use as async context manager
async with LLMService() as service:
    response = await service.generate(prompt="Hello")
```

## Configuration

The LLM service uses the following configuration from `app/core/config.py`:

```python
# Ollama endpoint
ollama_base_url: str = "http://localhost:11434"

# Default model
ollama_model: str = "codellama:7b"

# Request timeout (seconds)
ollama_timeout: int = 120

# Maximum retry attempts
ollama_max_retries: int = 3
```

These can be overridden via environment variables:
```bash
OLLAMA_BASE_URL=http://custom:11434
OLLAMA_MODEL=llama2:13b
OLLAMA_TIMEOUT=180
OLLAMA_MAX_RETRIES=5
```

## Error Handling Examples

```python
from app.services.llm_service import (
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelNotFoundError,
    OllamaGenerationError,
)

try:
    response = await service.generate(prompt="Test")
except OllamaConnectionError as e:
    # Ollama is not running or not accessible
    print(f"Connection error: {e}")
except OllamaTimeoutError as e:
    # Request took too long
    print(f"Timeout: {e}")
except OllamaModelNotFoundError as e:
    # Model not available
    print(f"Model not found: {e}")
except OllamaGenerationError as e:
    # Other generation errors
    print(f"Generation failed: {e}")
```

## Testing

The implementation includes comprehensive unit tests covering:
- Initialization and configuration
- Health checks
- Model listing and availability
- Text generation (streaming and non-streaming)
- Explanation modes and system prompts
- Timeout handling
- Exponential backoff retry logic
- Error handling
- Convenience methods

Run tests:
```bash
cd backend
python -m pytest tests/unit/test_llm_service.py -v
```

Test coverage: **85%**

## Examples

See `backend/examples/llm_service_example.py` for complete usage examples including:
1. Health checks
2. Listing models
3. Basic generation
4. Explanation modes
5. Streaming generation
6. Custom system prompts
7. Error handling

Run examples:
```bash
cd backend
python examples/llm_service_example.py
```

## Integration with FastAPI

For dependency injection in FastAPI endpoints:

```python
from fastapi import Depends
from app.services.llm_service import LLMService, get_llm_service

@app.post("/chat")
async def chat(
    message: str,
    service: LLMService = Depends(get_llm_service),
):
    response = await service.generate(
        prompt=message,
        explanation_mode=ExplanationMode.TECHNICAL,
    )
    return {"response": response}
```

## Requirements Satisfied

✅ **9.1**: Connect to configured Ollama instance  
✅ **9.2**: Return error if Ollama is unavailable  
✅ **9.3**: Support configurable model selection  
✅ **9.4**: Include system instructions for code-focused responses  
✅ **9.5**: Handle timeouts and retry with exponential backoff  
✅ **9.6**: Log errors and return user-friendly messages  
✅ **9.7**: Support streaming responses  
✅ **9.8**: Provide endpoint to list available models  

## Next Steps

The LLM service is now ready for integration with:
- **Task 2.32**: Chat service with RAG prompt construction
- **Task 2.40**: Code review service
- **Task 3.3**: Chat endpoints (API layer)
- **Task 3.5**: Code review endpoints (API layer)

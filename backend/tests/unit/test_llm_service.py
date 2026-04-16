"""
Unit tests for LLM service.

Tests the Ollama client wrapper including:
- Connection and health checks
- Model listing
- Text generation (streaming and non-streaming)
- Timeout handling
- Exponential backoff retry logic
- System prompt configuration
- Error handling
"""

import asyncio
import json
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.services.llm_service import (
    ExplanationMode,
    LLMService,
    OllamaConnectionError,
    OllamaError,
    OllamaGenerationError,
    OllamaModel,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    SYSTEM_PROMPTS,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        redis_url="redis://localhost:6379/0",
        celery_broker_url="redis://localhost:6379/1",
        celery_result_backend="redis://localhost:6379/2",
        secret_key="test-secret-key-minimum-32-characters-long",
        ollama_base_url="http://localhost:11434",
        ollama_model="codellama:7b",
        ollama_timeout=120,
        ollama_max_retries=3,
    )


@pytest.fixture
async def llm_service(mock_settings):
    """Create LLM service instance for testing."""
    service = LLMService(settings=mock_settings)
    yield service
    await service.close()


@pytest.fixture
def mock_httpx_client():
    """Create mock httpx client."""
    return AsyncMock(spec=httpx.AsyncClient)


# ============================================================================
# Test Initialization
# ============================================================================


def test_llm_service_initialization(mock_settings):
    """Test LLM service initializes with correct settings."""
    service = LLMService(settings=mock_settings)
    
    assert service.base_url == "http://localhost:11434"
    assert service.default_model == "codellama:7b"
    assert service.timeout == 120
    assert service.max_retries == 3
    assert isinstance(service.client, httpx.AsyncClient)


def test_llm_service_uses_global_settings():
    """Test LLM service uses global settings when not provided."""
    with patch("app.services.llm_service.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.ollama_base_url = "http://test:11434"
        mock_settings.ollama_model = "test-model"
        mock_settings.ollama_timeout = 60
        mock_settings.ollama_max_retries = 2
        mock_get_settings.return_value = mock_settings
        
        service = LLMService()
        
        assert service.base_url == "http://test:11434"
        assert service.default_model == "test-model"
        assert service.timeout == 60
        assert service.max_retries == 2


# ============================================================================
# Test Health Check
# ============================================================================


@pytest.mark.asyncio
async def test_health_check_success(llm_service):
    """Test health check succeeds when Ollama is available."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(llm_service.client, "get", return_value=mock_response):
        result = await llm_service.health_check()
        
        assert result is True
        llm_service.client.get.assert_called_once_with("/api/tags", timeout=5.0)


@pytest.mark.asyncio
async def test_health_check_failure(llm_service):
    """Test health check fails when Ollama is unavailable."""
    with patch.object(
        llm_service.client,
        "get",
        side_effect=httpx.ConnectError("Connection refused"),
    ):
        result = await llm_service.health_check()
        
        assert result is False


@pytest.mark.asyncio
async def test_ensure_available_success(llm_service):
    """Test ensure_available succeeds when Ollama is healthy."""
    with patch.object(llm_service, "health_check", return_value=True):
        await llm_service.ensure_available()  # Should not raise


@pytest.mark.asyncio
async def test_ensure_available_failure(llm_service):
    """Test ensure_available raises exception when Ollama is unavailable."""
    with patch.object(llm_service, "health_check", return_value=False):
        with pytest.raises(OllamaConnectionError) as exc_info:
            await llm_service.ensure_available()
        
        assert "Unable to connect to Ollama" in str(exc_info.value)


# ============================================================================
# Test Model Management
# ============================================================================


@pytest.mark.asyncio
async def test_list_models_success(llm_service):
    """Test listing models returns available models."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [
            {
                "name": "codellama:7b",
                "modified_at": "2024-01-01T00:00:00Z",
                "size": 3800000000,
                "digest": "abc123",
            },
            {
                "name": "llama2:13b",
                "modified_at": "2024-01-02T00:00:00Z",
                "size": 7300000000,
                "digest": "def456",
            },
        ]
    }
    
    with patch.object(llm_service, "_retry_request", return_value=mock_response):
        models = await llm_service.list_models()
        
        assert len(models) == 2
        assert models[0].name == "codellama:7b"
        assert models[1].name == "llama2:13b"
        assert models[0].size == 3800000000


@pytest.mark.asyncio
async def test_list_models_failure(llm_service):
    """Test listing models raises exception on failure."""
    with patch.object(
        llm_service,
        "_retry_request",
        side_effect=httpx.HTTPError("Connection failed"),
    ):
        with pytest.raises(OllamaError) as exc_info:
            await llm_service.list_models()
        
        assert "Failed to list models" in str(exc_info.value)


@pytest.mark.asyncio
async def test_check_model_available_exists(llm_service):
    """Test check_model_available returns True for existing model."""
    mock_models = [
        OllamaModel(
            name="codellama:7b",
            modified_at="2024-01-01T00:00:00Z",
            size=3800000000,
            digest="abc123",
        ),
    ]
    
    with patch.object(llm_service, "list_models", return_value=mock_models):
        result = await llm_service.check_model_available("codellama:7b")
        
        assert result is True


@pytest.mark.asyncio
async def test_check_model_available_not_exists(llm_service):
    """Test check_model_available returns False for non-existing model."""
    mock_models = [
        OllamaModel(
            name="codellama:7b",
            modified_at="2024-01-01T00:00:00Z",
            size=3800000000,
            digest="abc123",
        ),
    ]
    
    with patch.object(llm_service, "list_models", return_value=mock_models):
        result = await llm_service.check_model_available("nonexistent:1b")
        
        assert result is False


# ============================================================================
# Test Text Generation
# ============================================================================


@pytest.mark.asyncio
async def test_generate_success(llm_service):
    """Test successful text generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "codellama:7b",
        "response": "This is a test response.",
        "done": True,
        "eval_count": 10,
        "eval_duration": 1000000000,  # 1 second in nanoseconds
    }
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(llm_service, "_retry_request", return_value=mock_response):
            result = await llm_service.generate(
                prompt="Test prompt",
                temperature=0.7,
            )
            
            assert result == "This is a test response."


@pytest.mark.asyncio
async def test_generate_with_custom_model(llm_service):
    """Test generation with custom model."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "llama2:13b",
        "response": "Custom model response.",
        "done": True,
    }
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(llm_service, "_retry_request", return_value=mock_response):
            result = await llm_service.generate(
                prompt="Test prompt",
                model="llama2:13b",
            )
            
            assert result == "Custom model response."


@pytest.mark.asyncio
async def test_generate_with_explanation_mode(llm_service):
    """Test generation with explanation mode sets system prompt."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "codellama:7b",
        "response": "Beginner-friendly response.",
        "done": True,
    }
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(llm_service, "_retry_request", return_value=mock_response) as mock_retry:
            result = await llm_service.generate(
                prompt="Test prompt",
                explanation_mode=ExplanationMode.BEGINNER,
            )
            
            # Check that system prompt was included
            call_args = mock_retry.call_args
            request_json = call_args.kwargs["json"]
            assert request_json["system"] == SYSTEM_PROMPTS[ExplanationMode.BEGINNER]


@pytest.mark.asyncio
async def test_generate_with_custom_system_prompt(llm_service):
    """Test generation with custom system prompt overrides explanation mode."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "codellama:7b",
        "response": "Custom prompt response.",
        "done": True,
    }
    
    custom_prompt = "You are a custom assistant."
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(llm_service, "_retry_request", return_value=mock_response) as mock_retry:
            result = await llm_service.generate(
                prompt="Test prompt",
                system_prompt=custom_prompt,
                explanation_mode=ExplanationMode.BEGINNER,  # Should be ignored
            )
            
            # Check that custom system prompt was used
            call_args = mock_retry.call_args
            request_json = call_args.kwargs["json"]
            assert request_json["system"] == custom_prompt


@pytest.mark.asyncio
async def test_generate_timeout_error(llm_service):
    """Test generation raises timeout error on timeout."""
    with patch.object(llm_service, "ensure_available"):
        with patch.object(
            llm_service,
            "_retry_request",
            side_effect=httpx.TimeoutException("Request timed out"),
        ):
            with pytest.raises(OllamaTimeoutError) as exc_info:
                await llm_service.generate(prompt="Test prompt")
            
            assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_generate_model_not_found(llm_service):
    """Test generation raises model not found error."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Model not found"
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(
            llm_service,
            "_retry_request",
            side_effect=httpx.HTTPStatusError(
                "Not found",
                request=MagicMock(),
                response=mock_response,
            ),
        ):
            with pytest.raises(OllamaModelNotFoundError) as exc_info:
                await llm_service.generate(
                    prompt="Test prompt",
                    model="nonexistent:1b",
                )
            
            assert "not available" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_generate_unexpected_error(llm_service):
    """Test generation handles unexpected errors gracefully."""
    with patch.object(llm_service, "ensure_available"):
        with patch.object(
            llm_service,
            "_retry_request",
            side_effect=Exception("Unexpected error"),
        ):
            with pytest.raises(OllamaGenerationError) as exc_info:
                await llm_service.generate(prompt="Test prompt")
            
            assert "unexpected error" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_generate_rejects_stream_flag(llm_service):
    """Test generate raises error if stream=True is passed."""
    with pytest.raises(ValueError) as exc_info:
        await llm_service.generate(prompt="Test prompt", stream=True)
    
    assert "generate_stream" in str(exc_info.value)


# ============================================================================
# Test Streaming Generation
# ============================================================================


@pytest.mark.asyncio
async def test_generate_stream_success(llm_service):
    """Test successful streaming generation."""
    # Mock streaming response
    mock_lines = [
        '{"model":"codellama:7b","response":"Hello","done":false}',
        '{"model":"codellama:7b","response":" world","done":false}',
        '{"model":"codellama:7b","response":"!","done":true,"eval_count":3,"eval_duration":1000000000}',
    ]
    
    async def mock_aiter_lines():
        for line in mock_lines:
            yield line
    
    mock_response = MagicMock()
    mock_response.aiter_lines = mock_aiter_lines
    mock_response.raise_for_status = MagicMock()
    
    mock_stream_context = AsyncMock()
    mock_stream_context.__aenter__.return_value = mock_response
    mock_stream_context.__aexit__.return_value = None
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(llm_service.client, "stream", return_value=mock_stream_context):
            chunks = []
            async for chunk in llm_service.generate_stream(prompt="Test prompt"):
                chunks.append(chunk)
            
            assert chunks == ["Hello", " world", "!"]


@pytest.mark.asyncio
async def test_generate_stream_with_explanation_mode(llm_service):
    """Test streaming with explanation mode."""
    mock_lines = [
        '{"model":"codellama:7b","response":"Test","done":true}',
    ]
    
    async def mock_aiter_lines():
        for line in mock_lines:
            yield line
    
    mock_response = MagicMock()
    mock_response.aiter_lines = mock_aiter_lines
    mock_response.raise_for_status = MagicMock()
    
    mock_stream_context = AsyncMock()
    mock_stream_context.__aenter__.return_value = mock_response
    mock_stream_context.__aexit__.return_value = None
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(llm_service.client, "stream", return_value=mock_stream_context) as mock_stream:
            chunks = []
            async for chunk in llm_service.generate_stream(
                prompt="Test prompt",
                explanation_mode=ExplanationMode.TECHNICAL,
            ):
                chunks.append(chunk)
            
            # Check that system prompt was included
            call_args = mock_stream.call_args
            request_json = call_args.kwargs["json"]
            assert request_json["system"] == SYSTEM_PROMPTS[ExplanationMode.TECHNICAL]


@pytest.mark.asyncio
async def test_generate_stream_timeout(llm_service):
    """Test streaming raises timeout error."""
    mock_stream_context = AsyncMock()
    mock_stream_context.__aenter__.side_effect = httpx.TimeoutException("Timeout")
    
    with patch.object(llm_service, "ensure_available"):
        with patch.object(llm_service.client, "stream", return_value=mock_stream_context):
            with pytest.raises(OllamaTimeoutError):
                async for _ in llm_service.generate_stream(prompt="Test prompt"):
                    pass


# ============================================================================
# Test Retry Logic
# ============================================================================


@pytest.mark.asyncio
async def test_retry_request_success_first_attempt(llm_service):
    """Test retry succeeds on first attempt."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(llm_service.client, "request", return_value=mock_response):
        result = await llm_service._retry_request("GET", "/test")
        
        assert result == mock_response
        llm_service.client.request.assert_called_once()


@pytest.mark.asyncio
async def test_retry_request_success_after_retries(llm_service):
    """Test retry succeeds after transient failures."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    
    # Fail twice, then succeed
    side_effects = [
        httpx.TimeoutException("Timeout"),
        httpx.ConnectError("Connection failed"),
        mock_response,
    ]
    
    with patch.object(llm_service.client, "request", side_effect=side_effects):
        with patch("asyncio.sleep"):  # Mock sleep to speed up test
            result = await llm_service._retry_request("GET", "/test")
            
            assert result == mock_response
            assert llm_service.client.request.call_count == 3


@pytest.mark.asyncio
async def test_retry_request_exhausts_retries(llm_service):
    """Test retry exhausts all attempts and raises exception."""
    with patch.object(
        llm_service.client,
        "request",
        side_effect=httpx.TimeoutException("Timeout"),
    ):
        with patch("asyncio.sleep"):  # Mock sleep to speed up test
            with pytest.raises(httpx.TimeoutException):
                await llm_service._retry_request("GET", "/test")
            
            # Should try max_retries + 1 times (initial + retries)
            assert llm_service.client.request.call_count == llm_service.max_retries + 1


@pytest.mark.asyncio
async def test_retry_request_no_retry_on_4xx(llm_service):
    """Test retry does not retry on 4xx client errors."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    
    with patch.object(
        llm_service.client,
        "request",
        side_effect=httpx.HTTPStatusError(
            "Bad request",
            request=MagicMock(),
            response=mock_response,
        ),
    ):
        with pytest.raises(httpx.HTTPStatusError):
            await llm_service._retry_request("GET", "/test")
        
        # Should only try once (no retries for 4xx)
        llm_service.client.request.assert_called_once()


@pytest.mark.asyncio
async def test_retry_request_exponential_backoff(llm_service):
    """Test retry uses exponential backoff delays."""
    with patch.object(
        llm_service.client,
        "request",
        side_effect=httpx.TimeoutException("Timeout"),
    ):
        with patch("asyncio.sleep") as mock_sleep:
            with pytest.raises(httpx.TimeoutException):
                await llm_service._retry_request("GET", "/test")
            
            # Check exponential backoff: 1s, 2s, 4s
            sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
            assert sleep_calls == [1, 2, 4]


# ============================================================================
# Test Convenience Methods
# ============================================================================


@pytest.mark.asyncio
async def test_generate_with_mode(llm_service):
    """Test generate_with_mode convenience method."""
    with patch.object(llm_service, "generate", return_value="Test response") as mock_generate:
        result = await llm_service.generate_with_mode(
            prompt="Test prompt",
            explanation_mode=ExplanationMode.INTERVIEW,
        )
        
        assert result == "Test response"
        mock_generate.assert_called_once_with(
            prompt="Test prompt",
            explanation_mode=ExplanationMode.INTERVIEW,
        )


@pytest.mark.asyncio
async def test_generate_code_explanation(llm_service):
    """Test generate_code_explanation convenience method."""
    with patch.object(llm_service, "generate", return_value="Code explanation") as mock_generate:
        result = await llm_service.generate_code_explanation(
            code="def hello(): pass",
            question="What does this do?",
            explanation_mode=ExplanationMode.BEGINNER,
        )
        
        assert result == "Code explanation"
        
        # Check that prompt includes code and question
        call_args = mock_generate.call_args
        prompt = call_args.kwargs["prompt"]
        assert "def hello(): pass" in prompt
        assert "What does this do?" in prompt


# ============================================================================
# Test System Prompts
# ============================================================================


def test_system_prompts_defined():
    """Test all explanation modes have system prompts."""
    for mode in ExplanationMode:
        assert mode in SYSTEM_PROMPTS
        assert isinstance(SYSTEM_PROMPTS[mode], str)
        assert len(SYSTEM_PROMPTS[mode]) > 0


def test_system_prompts_content():
    """Test system prompts contain expected keywords."""
    assert "tutor" in SYSTEM_PROMPTS[ExplanationMode.BEGINNER].lower()
    assert "expert" in SYSTEM_PROMPTS[ExplanationMode.TECHNICAL].lower()
    assert "interviewer" in SYSTEM_PROMPTS[ExplanationMode.INTERVIEW].lower()

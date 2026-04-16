"""
Tests for chat API endpoints.

This module tests the chat endpoints including:
- POST /api/v1/chat (streaming and non-streaming)
- GET /api/v1/chat/sessions/{id}
- DELETE /api/v1/chat/sessions/{id}
- GET /api/v1/chat/sessions
"""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.chat_service import ChatMessage, ChatSession, Citation
from app.services.llm_service import ExplanationMode


@pytest.fixture
def mock_chat_service():
    """Mock chat service for testing."""
    service = MagicMock()
    
    # Mock session
    session = ChatSession(
        session_id="test-session-id",
        repository_ids=[uuid.uuid4()],
        messages=[],
        explanation_mode=ExplanationMode.TECHNICAL,
        created_at=MagicMock(),
        updated_at=MagicMock(),
    )
    
    # Mock citation
    citation = Citation(
        chunk_id=uuid.uuid4(),
        repository_id=uuid.uuid4(),
        file_path="test.py",
        start_line=1,
        end_line=10,
        language="python",
        content="def test(): pass",
        score=0.95,
    )
    
    # Configure mock methods
    service.chat = AsyncMock(return_value=(
        "This is a test response",
        [citation],
        "test-session-id"
    ))
    
    service.get_session = AsyncMock(return_value=session)
    service.delete_session = AsyncMock(return_value=True)
    service.list_sessions = AsyncMock(return_value=["session-1", "session-2"])
    
    return service


@pytest.mark.asyncio
async def test_chat_non_streaming(mock_chat_service):
    """Test non-streaming chat endpoint."""
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    "message": "What does this code do?",
                    "repository_ids": [str(uuid.uuid4())],
                    "explanation_mode": "technical",
                    "top_k": 5,
                    "stream": False,
                }
            )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "response" in data
    assert "citations" in data
    assert "session_id" in data
    assert data["response"] == "This is a test response"
    assert len(data["citations"]) == 1
    assert data["session_id"] == "test-session-id"


@pytest.mark.asyncio
async def test_chat_streaming(mock_chat_service):
    """Test streaming chat endpoint."""
    # Mock streaming response
    async def mock_stream(*args, **kwargs):
        citation = Citation(
            chunk_id=uuid.uuid4(),
            repository_id=uuid.uuid4(),
            file_path="test.py",
            start_line=1,
            end_line=10,
            language="python",
            content="def test(): pass",
            score=0.95,
        )
        
        # First chunk with citations
        yield "This ", [citation], "test-session-id"
        # Subsequent chunks
        yield "is ", None, None
        yield "a ", None, None
        yield "test", None, None
    
    mock_chat_service.chat_stream = mock_stream
    
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    "message": "What does this code do?",
                    "repository_ids": [str(uuid.uuid4())],
                    "explanation_mode": "technical",
                    "top_k": 5,
                    "stream": True,
                }
            )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


@pytest.mark.asyncio
async def test_get_session(mock_chat_service):
    """Test get session endpoint."""
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/chat/sessions/test-session-id")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "session_id" in data
    assert "repository_ids" in data
    assert "messages" in data
    assert "explanation_mode" in data
    assert data["session_id"] == "test-session-id"


@pytest.mark.asyncio
async def test_get_session_not_found(mock_chat_service):
    """Test get session endpoint with non-existent session."""
    mock_chat_service.get_session = AsyncMock(return_value=None)
    
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/chat/sessions/nonexistent")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "error" in data["detail"]


@pytest.mark.asyncio
async def test_delete_session(mock_chat_service):
    """Test delete session endpoint."""
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/v1/chat/sessions/test-session-id")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "message" in data
    assert "deleted_session_id" in data
    assert data["deleted_session_id"] == "test-session-id"


@pytest.mark.asyncio
async def test_delete_session_not_found(mock_chat_service):
    """Test delete session endpoint with non-existent session."""
    mock_chat_service.get_session = AsyncMock(return_value=None)
    
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/v1/chat/sessions/nonexistent")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_list_sessions(mock_chat_service):
    """Test list sessions endpoint."""
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/chat/sessions")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "sessions" in data
    assert "total" in data
    assert len(data["sessions"]) == 2
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_chat_invalid_request():
    """Test chat endpoint with invalid request."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "message": "",  # Empty message (invalid)
                "repository_ids": [],  # Empty list (invalid)
            }
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_chat_ollama_unavailable(mock_chat_service):
    """Test chat endpoint when Ollama is unavailable."""
    from app.services.llm_service import OllamaConnectionError
    
    mock_chat_service.chat = AsyncMock(
        side_effect=OllamaConnectionError("Unable to connect to Ollama")
    )
    
    with patch("app.api.routes.chat.get_chat_service", return_value=mock_chat_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/chat",
                json={
                    "message": "What does this code do?",
                    "repository_ids": [str(uuid.uuid4())],
                    "stream": False,
                }
            )
    
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.json()
    assert "error" in data["detail"]
    assert data["detail"]["error"] == "LLM service unavailable"

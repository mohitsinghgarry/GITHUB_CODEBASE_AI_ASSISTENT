"""
Unit tests for chat service.

This module tests the chat service functionality including:
- Session management
- RAG prompt construction
- Citation building
- Token limit truncation
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.chat_service import (
    ChatService,
    ChatSession,
    ChatMessage,
    Citation,
    ExplanationMode,
)


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    client = AsyncMock()
    client.save_session = AsyncMock(return_value=True)
    client.get_session = AsyncMock(return_value=None)
    client.delete_session = AsyncMock(return_value=True)
    client.list_sessions = AsyncMock(return_value=[])
    return client


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = AsyncMock()
    service.generate = AsyncMock(return_value="This is a test response.")
    service.generate_stream = AsyncMock()
    return service


@pytest.fixture
def mock_search_service():
    """Create a mock search service."""
    service = AsyncMock()
    service.search_hybrid = AsyncMock(return_value=[
        {
            "chunk_id": str(uuid.uuid4()),
            "repository_id": str(uuid.uuid4()),
            "file_path": "test.py",
            "start_line": 1,
            "end_line": 10,
            "language": "python",
            "content": "def test():\n    pass",
            "rrf_score": 0.95,
        }
    ])
    return service


@pytest.fixture
def chat_service(mock_redis_client, mock_llm_service, mock_search_service):
    """Create a chat service with mocked dependencies."""
    return ChatService(
        redis_client=mock_redis_client,
        llm_service=mock_llm_service,
        search_service=mock_search_service,
    )


class TestChatService:
    """Test suite for ChatService."""
    
    @pytest.mark.asyncio
    async def test_create_session(self, chat_service, mock_redis_client):
        """Test creating a new chat session."""
        repo_ids = [uuid.uuid4()]
        
        session = await chat_service.create_session(
            repository_ids=repo_ids,
            explanation_mode=ExplanationMode.TECHNICAL,
        )
        
        assert session.session_id is not None
        assert session.repository_ids == repo_ids
        assert session.explanation_mode == ExplanationMode.TECHNICAL
        assert len(session.messages) == 0
        
        # Verify Redis save was called
        mock_redis_client.save_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, chat_service, mock_redis_client):
        """Test getting a session that doesn't exist."""
        mock_redis_client.get_session.return_value = None
        
        session = await chat_service.get_session("nonexistent-id")
        
        assert session is None
    
    @pytest.mark.asyncio
    async def test_get_session_found(self, chat_service, mock_redis_client):
        """Test getting an existing session."""
        session_id = str(uuid.uuid4())
        repo_id = str(uuid.uuid4())
        
        mock_redis_client.get_session.return_value = {
            "session_id": session_id,
            "repository_ids": [repo_id],
            "messages": [],
            "explanation_mode": "technical",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        session = await chat_service.get_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert len(session.repository_ids) == 1
    
    @pytest.mark.asyncio
    async def test_delete_session(self, chat_service, mock_redis_client):
        """Test deleting a session."""
        session_id = str(uuid.uuid4())
        
        result = await chat_service.delete_session(session_id)
        
        assert result is True
        mock_redis_client.delete_session.assert_called_once_with(session_id)
    
    def test_estimate_tokens(self, chat_service):
        """Test token estimation."""
        text = "This is a test string with some words."
        tokens = chat_service._estimate_tokens(text)
        
        # Should be roughly len(text) / 4
        assert tokens > 0
        assert tokens == len(text) // 4
    
    def test_truncate_to_token_limit(self, chat_service):
        """Test text truncation to token limit."""
        text = "A" * 1000  # 1000 characters
        max_tokens = 50  # Should allow ~200 characters
        
        truncated = chat_service._truncate_to_token_limit(text, max_tokens)
        
        assert len(truncated) < len(text)
        assert truncated.endswith("... [truncated]")
    
    def test_truncate_to_token_limit_no_truncation(self, chat_service):
        """Test that short text is not truncated."""
        text = "Short text"
        max_tokens = 100
        
        truncated = chat_service._truncate_to_token_limit(text, max_tokens)
        
        assert truncated == text
    
    def test_build_citations(self, chat_service):
        """Test building citations from search results."""
        chunk_id = uuid.uuid4()
        repo_id = uuid.uuid4()
        
        search_results = [
            {
                "chunk_id": str(chunk_id),
                "repository_id": str(repo_id),
                "file_path": "test.py",
                "start_line": 1,
                "end_line": 10,
                "language": "python",
                "content": "def test():\n    pass",
                "rrf_score": 0.95,
            }
        ]
        
        citations = chat_service._build_citations(search_results)
        
        assert len(citations) == 1
        assert citations[0].chunk_id == chunk_id
        assert citations[0].repository_id == repo_id
        assert citations[0].file_path == "test.py"
        assert citations[0].score == 0.95
    
    def test_format_code_context(self, chat_service):
        """Test formatting code context from citations."""
        citation = Citation(
            chunk_id=uuid.uuid4(),
            repository_id=uuid.uuid4(),
            file_path="test.py",
            start_line=1,
            end_line=5,
            language="python",
            content="def test():\n    return True",
            score=0.95,
        )
        
        context = chat_service._format_code_context([citation], max_tokens=500)
        
        assert "[Source 1]" in context
        assert "test.py" in context
        assert "lines 1-5" in context
        assert "def test():" in context
        assert "```python" in context
    
    def test_format_code_context_empty(self, chat_service):
        """Test formatting code context with no citations."""
        context = chat_service._format_code_context([], max_tokens=500)
        
        assert context == "No relevant code found."
    
    def test_build_rag_prompt(self, chat_service):
        """Test building RAG prompt."""
        user_question = "What does this function do?"
        code_context = "```python\ndef test():\n    pass\n```"
        
        prompt = chat_service._build_rag_prompt(
            user_question=user_question,
            code_context=code_context,
        )
        
        assert "relevant code from the repository" in prompt
        assert user_question in prompt
        assert code_context in prompt
        assert "Reference specific source numbers" in prompt
    
    def test_build_rag_prompt_with_history(self, chat_service):
        """Test building RAG prompt with conversation history."""
        user_question = "What does this function do?"
        code_context = "```python\ndef test():\n    pass\n```"
        conversation_history = "User: Previous question\nAssistant: Previous answer\n"
        
        prompt = chat_service._build_rag_prompt(
            user_question=user_question,
            code_context=code_context,
            conversation_history=conversation_history,
        )
        
        assert "Previous conversation:" in prompt
        assert conversation_history in prompt
    
    def test_truncate_conversation_history(self, chat_service):
        """Test truncating conversation history."""
        messages = [
            ChatMessage(
                role="user",
                content="Question 1",
                timestamp=datetime.utcnow(),
            ),
            ChatMessage(
                role="assistant",
                content="Answer 1",
                timestamp=datetime.utcnow(),
            ),
            ChatMessage(
                role="user",
                content="Question 2",
                timestamp=datetime.utcnow(),
            ),
        ]
        
        history = chat_service._truncate_conversation_history(messages, max_tokens=50)
        
        # Should include most recent messages
        assert "Question 2" in history
        assert len(history) > 0
    
    def test_truncate_conversation_history_empty(self, chat_service):
        """Test truncating empty conversation history."""
        history = chat_service._truncate_conversation_history([], max_tokens=100)
        
        assert history == ""
    
    @pytest.mark.asyncio
    async def test_chat(
        self,
        chat_service,
        mock_redis_client,
        mock_llm_service,
        mock_search_service,
    ):
        """Test chat functionality."""
        repo_ids = [uuid.uuid4()]
        user_message = "What does this code do?"
        
        response, citations, session_id = await chat_service.chat(
            session_id=None,
            user_message=user_message,
            repository_ids=repo_ids,
            explanation_mode=ExplanationMode.TECHNICAL,
            top_k=5,
        )
        
        # Verify response
        assert response == "This is a test response."
        assert len(citations) == 1
        assert session_id is not None
        
        # Verify search was called
        mock_search_service.search_hybrid.assert_called_once()
        
        # Verify LLM was called
        mock_llm_service.generate.assert_called_once()
        
        # Verify session was saved
        assert mock_redis_client.save_session.call_count >= 2  # Create + update
    
    @pytest.mark.asyncio
    async def test_chat_with_existing_session(
        self,
        chat_service,
        mock_redis_client,
        mock_llm_service,
        mock_search_service,
    ):
        """Test chat with an existing session."""
        session_id = str(uuid.uuid4())
        repo_id = uuid.uuid4()
        
        # Mock existing session
        mock_redis_client.get_session.return_value = {
            "session_id": session_id,
            "repository_ids": [str(repo_id)],
            "messages": [
                {
                    "role": "user",
                    "content": "Previous question",
                    "timestamp": datetime.utcnow().isoformat(),
                    "citations": None,
                }
            ],
            "explanation_mode": "technical",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        response, citations, returned_session_id = await chat_service.chat(
            session_id=session_id,
            user_message="Follow-up question",
            repository_ids=[repo_id],
            explanation_mode=ExplanationMode.TECHNICAL,
        )
        
        assert returned_session_id == session_id
        assert response == "This is a test response."
        
        # Verify session was retrieved
        mock_redis_client.get_session.assert_called_once_with(session_id)


class TestChatMessage:
    """Test suite for ChatMessage."""
    
    def test_to_dict(self):
        """Test converting message to dictionary."""
        message = ChatMessage(
            role="user",
            content="Test message",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            citations=None,
        )
        
        data = message.to_dict()
        
        assert data["role"] == "user"
        assert data["content"] == "Test message"
        assert data["timestamp"] == "2024-01-01T12:00:00"
        assert data["citations"] is None
    
    def test_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            "role": "assistant",
            "content": "Test response",
            "timestamp": "2024-01-01T12:00:00",
            "citations": [],
        }
        
        message = ChatMessage.from_dict(data)
        
        assert message.role == "assistant"
        assert message.content == "Test response"
        assert message.timestamp == datetime(2024, 1, 1, 12, 0, 0)
        assert message.citations == []


class TestChatSession:
    """Test suite for ChatSession."""
    
    def test_to_dict(self):
        """Test converting session to dictionary."""
        session_id = str(uuid.uuid4())
        repo_id = uuid.uuid4()
        
        session = ChatSession(
            session_id=session_id,
            repository_ids=[repo_id],
            messages=[],
            explanation_mode=ExplanationMode.TECHNICAL,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        
        data = session.to_dict()
        
        assert data["session_id"] == session_id
        assert data["repository_ids"] == [str(repo_id)]
        assert data["messages"] == []
        assert data["explanation_mode"] == "technical"
    
    def test_from_dict(self):
        """Test creating session from dictionary."""
        session_id = str(uuid.uuid4())
        repo_id = str(uuid.uuid4())
        
        data = {
            "session_id": session_id,
            "repository_ids": [repo_id],
            "messages": [],
            "explanation_mode": "technical",
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00",
        }
        
        session = ChatSession.from_dict(data)
        
        assert session.session_id == session_id
        assert len(session.repository_ids) == 1
        assert session.explanation_mode == ExplanationMode.TECHNICAL


class TestCitation:
    """Test suite for Citation."""
    
    def test_to_dict(self):
        """Test converting citation to dictionary."""
        chunk_id = uuid.uuid4()
        repo_id = uuid.uuid4()
        
        citation = Citation(
            chunk_id=chunk_id,
            repository_id=repo_id,
            file_path="test.py",
            start_line=1,
            end_line=10,
            language="python",
            content="def test():\n    pass",
            score=0.95,
        )
        
        data = citation.to_dict()
        
        assert data["chunk_id"] == str(chunk_id)
        assert data["repository_id"] == str(repo_id)
        assert data["file_path"] == "test.py"
        assert data["start_line"] == 1
        assert data["end_line"] == 10
        assert data["language"] == "python"
        assert data["score"] == 0.95

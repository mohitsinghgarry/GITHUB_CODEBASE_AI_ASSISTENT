"""
Chat service with RAG prompt construction and session management.

This module implements the chat service for the GitHub Codebase RAG Assistant.
It handles:
- Session management with Redis
- RAG prompt construction with system instructions, retrieved chunks, and user questions
- Citation linking to source chunks
- Token limit truncation logic
- Conversation history management

Requirements:
- 6.1: Create or retrieve a Chat_Session
- 6.2: Retrieve relevant Code_Chunks using semantic search
- 6.3: Construct a prompt with code context and user question
- 6.4: Send prompt to Ollama for inference
- 6.5: Return response with citations to source Code_Chunks
- 6.6: Maintain Chat_Session history for context-aware follow-up questions
- 6.7: Summarize or truncate older messages when session exceeds token limits
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

from app.core.config import Settings, get_settings
from app.core.redis_client import RedisClient, get_redis_client
from app.services.llm_service import ExplanationMode, LLMService
from app.services.search_service import UnifiedSearchService

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class ChatMessage:
    """
    Represents a single message in a chat session.
    
    Attributes:
        role: Message role ('user' or 'assistant')
        content: Message content
        timestamp: When the message was created
        citations: List of source chunk citations (for assistant messages)
    """
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    citations: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "citations": self.citations,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create message from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            citations=data.get("citations"),
        )


@dataclass
class ChatSession:
    """
    Represents a chat session with conversation history.
    
    Attributes:
        session_id: Unique session identifier
        repository_ids: List of repository IDs to search in
        messages: List of chat messages
        explanation_mode: Explanation mode for responses
        created_at: When the session was created
        updated_at: When the session was last updated
    """
    session_id: str
    repository_ids: List[uuid.UUID]
    messages: List[ChatMessage]
    explanation_mode: ExplanationMode
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "repository_ids": [str(repo_id) for repo_id in self.repository_ids],
            "messages": [msg.to_dict() for msg in self.messages],
            "explanation_mode": self.explanation_mode.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        """Create session from dictionary."""
        return cls(
            session_id=data["session_id"],
            repository_ids=[uuid.UUID(repo_id) for repo_id in data["repository_ids"]],
            messages=[ChatMessage.from_dict(msg) for msg in data["messages"]],
            explanation_mode=ExplanationMode(data["explanation_mode"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class Citation:
    """
    Represents a citation to a source code chunk.
    
    Attributes:
        chunk_id: Unique chunk identifier
        repository_id: Repository identifier
        file_path: Path to the source file
        start_line: Starting line number
        end_line: Ending line number
        language: Programming language
        content: Code content (may be truncated)
        score: Relevance score
    """
    chunk_id: uuid.UUID
    repository_id: uuid.UUID
    file_path: str
    start_line: int
    end_line: int
    language: Optional[str]
    content: str
    score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary."""
        return {
            "chunk_id": str(self.chunk_id),
            "repository_id": str(self.repository_id),
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "language": self.language,
            "content": self.content,
            "score": self.score,
        }


# ============================================================================
# Chat Service
# ============================================================================


class ChatService:
    """
    Service for managing chat sessions and RAG-based conversations.
    
    This service handles:
    - Session creation and retrieval
    - RAG prompt construction with retrieved code chunks
    - Citation linking to source chunks
    - Token limit management and truncation
    - Conversation history persistence
    
    Requirements:
    - 6.1: Create or retrieve a Chat_Session
    - 6.2: Retrieve relevant Code_Chunks using semantic search
    - 6.3: Construct a prompt with code context and user question
    - 6.4: Send prompt to Ollama for inference
    - 6.5: Return response with citations to source Code_Chunks
    - 6.6: Maintain Chat_Session history for context-aware follow-up questions
    - 6.7: Summarize or truncate older messages when session exceeds token limits
    """
    
    def __init__(
        self,
        redis_client: RedisClient,
        llm_service: LLMService,
        search_service: UnifiedSearchService,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize the chat service.
        
        Args:
            redis_client: Redis client for session storage
            llm_service: LLM service for text generation
            search_service: Search service for retrieving relevant chunks
            settings: Application settings (uses global settings if not provided)
        """
        self.redis_client = redis_client
        self.llm_service = llm_service
        self.search_service = search_service
        self.settings = settings or get_settings()
        
        # Token limits from settings
        self.max_context_tokens = self.settings.max_context_tokens
        self.max_response_tokens = self.settings.max_response_tokens
        
        # Approximate tokens per character (rough estimate: 1 token ≈ 4 characters)
        self.chars_per_token = 4
        
        logger.info(
            f"Initialized chat service with max_context_tokens={self.max_context_tokens}, "
            f"max_response_tokens={self.max_response_tokens}"
        )
    
    # ========================================================================
    # Session Management (Requirement 6.1, 6.6)
    # ========================================================================
    
    async def create_session(
        self,
        repository_ids: List[uuid.UUID],
        explanation_mode: ExplanationMode = ExplanationMode.TECHNICAL,
    ) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            repository_ids: List of repository IDs to search in
            explanation_mode: Explanation mode for responses
            
        Returns:
            ChatSession: The newly created session
            
        Requirement 6.1: Create or retrieve a Chat_Session
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = ChatSession(
            session_id=session_id,
            repository_ids=repository_ids,
            messages=[],
            explanation_mode=explanation_mode,
            created_at=now,
            updated_at=now,
        )
        
        # Save to Redis
        await self.redis_client.save_session(session_id, session.to_dict())
        
        logger.info(
            f"Created new chat session {session_id} for repositories {repository_ids}"
        )
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve an existing chat session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Optional[ChatSession]: The session if found, None otherwise
            
        Requirement 6.1: Create or retrieve a Chat_Session
        """
        session_data = await self.redis_client.get_session(session_id)
        
        if session_data:
            logger.debug(f"Retrieved session {session_id}")
            return ChatSession.from_dict(session_data)
        
        logger.debug(f"Session {session_id} not found")
        return None
    
    async def get_or_create_session(
        self,
        session_id: Optional[str],
        repository_ids: List[uuid.UUID],
        explanation_mode: ExplanationMode = ExplanationMode.TECHNICAL,
    ) -> ChatSession:
        """
        Get an existing session or create a new one.
        
        Args:
            session_id: Session identifier (creates new if None)
            repository_ids: List of repository IDs to search in
            explanation_mode: Explanation mode for responses
            
        Returns:
            ChatSession: The session (existing or newly created)
        """
        if session_id:
            session = await self.get_session(session_id)
            if session:
                return session
        
        # Create new session if not found or no session_id provided
        return await self.create_session(repository_ids, explanation_mode)
    
    async def update_session(self, session: ChatSession) -> bool:
        """
        Update an existing session in Redis.
        
        Args:
            session: Session to update
            
        Returns:
            bool: True if successful, False otherwise
            
        Requirement 6.6: Maintain Chat_Session history
        """
        session.updated_at = datetime.utcnow()
        return await self.redis_client.save_session(
            session.session_id,
            session.to_dict()
        )
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if deleted, False otherwise
        """
        result = await self.redis_client.delete_session(session_id)
        
        if result:
            logger.info(f"Deleted session {session_id}")
        
        return result
    
    async def list_sessions(self) -> List[str]:
        """
        List all active session IDs.
        
        Returns:
            List[str]: List of session IDs
        """
        return await self.redis_client.list_sessions()
    
    # ========================================================================
    # RAG Prompt Construction (Requirement 6.3)
    # ========================================================================
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in text.
        
        Uses a rough approximation: 1 token ≈ 4 characters.
        
        Args:
            text: Text to estimate
            
        Returns:
            int: Estimated token count
        """
        return len(text) // self.chars_per_token
    
    def _truncate_to_token_limit(
        self,
        text: str,
        max_tokens: int,
        suffix: str = "... [truncated]"
    ) -> str:
        """
        Truncate text to fit within token limit.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum number of tokens
            suffix: Suffix to add when truncating
            
        Returns:
            str: Truncated text
        """
        estimated_tokens = self._estimate_tokens(text)
        
        if estimated_tokens <= max_tokens:
            return text
        
        # Calculate character limit
        max_chars = max_tokens * self.chars_per_token - len(suffix)
        
        if max_chars <= 0:
            return suffix
        
        return text[:max_chars] + suffix
    
    def _build_citations(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Citation]:
        """
        Build citation objects from search results.
        
        Args:
            search_results: Search results from hybrid search
            
        Returns:
            List[Citation]: List of citations
            
        Requirement 6.5: Return response with citations to source Code_Chunks
        """
        citations = []
        
        for result in search_results:
            citation = Citation(
                chunk_id=uuid.UUID(result["chunk_id"]) if isinstance(result["chunk_id"], str) else result["chunk_id"],
                repository_id=uuid.UUID(result["repository_id"]) if isinstance(result["repository_id"], str) else result["repository_id"],
                file_path=result["file_path"],
                start_line=result["start_line"],
                end_line=result["end_line"],
                language=result.get("language"),
                content=result["content"],
                score=result.get("rrf_score", result.get("vector_score", 0.0)),
            )
            citations.append(citation)
        
        return citations
    
    def _format_code_context(
        self,
        citations: List[Citation],
        max_tokens: int,
    ) -> str:
        """
        Format code chunks into context string with token limit.
        
        Args:
            citations: List of citations to include
            max_tokens: Maximum tokens for context
            
        Returns:
            str: Formatted context string
            
        Requirement 6.3: Construct a prompt with code context and user question
        """
        if not citations:
            return "No relevant code found."
        
        context_parts = []
        total_tokens = 0
        
        for i, citation in enumerate(citations, 1):
            # Format citation header
            header = f"\n[Source {i}] {citation.file_path} (lines {citation.start_line}-{citation.end_line})"
            if citation.language:
                header += f" - {citation.language}"
            header += "\n"
            
            # Format code block
            code_block = f"```{citation.language or ''}\n{citation.content}\n```\n"
            
            # Combine header and code
            chunk_text = header + code_block
            chunk_tokens = self._estimate_tokens(chunk_text)
            
            # Check if adding this chunk would exceed limit
            if total_tokens + chunk_tokens > max_tokens:
                # Try to fit a truncated version
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 100:  # Only add if we have reasonable space
                    truncated_content = self._truncate_to_token_limit(
                        citation.content,
                        remaining_tokens - self._estimate_tokens(header) - 20,
                        suffix="... [content truncated]"
                    )
                    truncated_block = f"```{citation.language or ''}\n{truncated_content}\n```\n"
                    context_parts.append(header + truncated_block)
                break
            
            context_parts.append(chunk_text)
            total_tokens += chunk_tokens
        
        return "\n".join(context_parts)
    
    def _build_rag_prompt(
        self,
        user_question: str,
        code_context: str,
        conversation_history: Optional[str] = None,
    ) -> str:
        """
        Build RAG prompt with system instruction, code context, and user question.
        
        Args:
            user_question: User's question
            code_context: Formatted code context from retrieved chunks
            conversation_history: Optional conversation history
            
        Returns:
            str: Complete RAG prompt
            
        Requirement 6.3: Construct a prompt with code context and user question
        """
        prompt_parts = []
        
        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("Previous conversation:")
            prompt_parts.append(conversation_history)
            prompt_parts.append("")
        
        # Add code context
        prompt_parts.append("Here is the relevant code from the repository:")
        prompt_parts.append(code_context)
        prompt_parts.append("")
        
        # Add user question
        prompt_parts.append("User question:")
        prompt_parts.append(user_question)
        prompt_parts.append("")
        
        # Add instruction
        prompt_parts.append(
            "Please answer the question based on the provided code. "
            "Reference specific source numbers (e.g., [Source 1]) when citing code. "
            "If the code doesn't contain enough information to answer the question, "
            "say so clearly."
        )
        
        return "\n".join(prompt_parts)
    
    def _truncate_conversation_history(
        self,
        messages: List[ChatMessage],
        max_tokens: int,
    ) -> str:
        """
        Truncate conversation history to fit within token limit.
        
        Keeps the most recent messages and truncates older ones.
        
        Args:
            messages: List of chat messages
            max_tokens: Maximum tokens for history
            
        Returns:
            str: Formatted conversation history
            
        Requirement 6.7: Summarize or truncate older messages when session exceeds token limits
        """
        if not messages:
            return ""
        
        history_parts = []
        total_tokens = 0
        
        # Process messages in reverse order (most recent first)
        for message in reversed(messages):
            message_text = f"{message.role.capitalize()}: {message.content}\n"
            message_tokens = self._estimate_tokens(message_text)
            
            if total_tokens + message_tokens > max_tokens:
                # Add truncation notice if we're skipping messages
                if history_parts:
                    history_parts.append("[Earlier messages truncated...]\n")
                break
            
            history_parts.append(message_text)
            total_tokens += message_tokens
        
        # Reverse back to chronological order
        return "".join(reversed(history_parts))
    
    # ========================================================================
    # Chat Operations (Requirements 6.2, 6.4, 6.5)
    # ========================================================================
    
    async def chat(
        self,
        session_id: Optional[str],
        user_message: str,
        repository_ids: List[uuid.UUID],
        explanation_mode: ExplanationMode = ExplanationMode.TECHNICAL,
        top_k: int = 5,
        include_history: bool = True,
        model: Optional[str] = None,
    ) -> Tuple[str, List[Citation], str]:
        """
        Process a chat message and generate a response.
        
        Args:
            session_id: Session identifier (creates new if None)
            user_message: User's message/question
            repository_ids: List of repository IDs to search in
            explanation_mode: Explanation mode for response
            top_k: Number of code chunks to retrieve
            include_history: Whether to include conversation history in prompt
            
        Returns:
            Tuple[str, List[Citation], str]: (response, citations, session_id)
            
        Requirements:
        - 6.2: Retrieve relevant Code_Chunks using semantic search
        - 6.3: Construct a prompt with code context and user question
        - 6.4: Send prompt to Ollama for inference
        - 6.5: Return response with citations to source Code_Chunks
        - 6.6: Maintain Chat_Session history
        """
        # Get or create session (Requirement 6.1)
        session = await self.get_or_create_session(
            session_id,
            repository_ids,
            explanation_mode
        )
        
        # Retrieve relevant code chunks (Requirement 6.2)
        logger.info(f"Retrieving top {top_k} chunks for query: {user_message[:100]}...")
        search_results = await self.search_service.search_hybrid(
            query=user_message,
            top_k=top_k,
            repository_ids=repository_ids,
        )
        
        # Build citations (Requirement 6.5)
        citations = self._build_citations(search_results)
        logger.info(f"Retrieved {len(citations)} relevant code chunks")
        
        # Calculate token budget
        # Reserve tokens for: response, system prompt, user question, and overhead
        response_budget = self.max_response_tokens
        system_prompt_budget = 200  # Approximate
        question_budget = self._estimate_tokens(user_message) + 50
        overhead_budget = 100
        
        available_for_context = (
            self.max_context_tokens -
            response_budget -
            system_prompt_budget -
            question_budget -
            overhead_budget
        )
        
        # Allocate context budget between history and code
        if include_history and session.messages:
            history_budget = min(available_for_context // 3, 500)  # Max 500 tokens for history
            code_budget = available_for_context - history_budget
        else:
            history_budget = 0
            code_budget = available_for_context
        
        # Format code context (Requirement 6.3)
        code_context = self._format_code_context(citations, code_budget)
        
        # Format conversation history (Requirement 6.7)
        conversation_history = None
        if include_history and session.messages:
            conversation_history = self._truncate_conversation_history(
                session.messages,
                history_budget
            )
        
        # Build RAG prompt (Requirement 6.3)
        prompt = self._build_rag_prompt(
            user_question=user_message,
            code_context=code_context,
            conversation_history=conversation_history,
        )
        
        logger.debug(f"Built RAG prompt with {self._estimate_tokens(prompt)} estimated tokens")
        
        # Generate response (Requirement 6.4)
        logger.info("Generating response from LLM...")
        response = await self.llm_service.generate(
            prompt=prompt,
            model=model,
            explanation_mode=explanation_mode,
            temperature=self.settings.rag_temperature,
            max_tokens=self.max_response_tokens,
        )
        
        logger.info(f"Generated response with {len(response)} characters")
        
        # Add messages to session history (Requirement 6.6)
        session.messages.append(ChatMessage(
            role="user",
            content=user_message,
            timestamp=datetime.utcnow(),
        ))
        
        session.messages.append(ChatMessage(
            role="assistant",
            content=response,
            timestamp=datetime.utcnow(),
            citations=[c.to_dict() for c in citations],
        ))
        
        # Update session in Redis
        await self.update_session(session)
        
        return response, citations, session.session_id
    
    async def chat_stream(
        self,
        session_id: Optional[str],
        user_message: str,
        repository_ids: List[uuid.UUID],
        explanation_mode: ExplanationMode = ExplanationMode.TECHNICAL,
        top_k: int = 5,
        include_history: bool = True,
        model: Optional[str] = None,
    ) -> AsyncIterator[Tuple[str, Optional[List[Citation]], Optional[str]]]:
        """
        Process a chat message and stream the response.
        
        Yields tuples of (chunk, citations, session_id).
        Citations and session_id are only included in the first chunk.
        
        Args:
            session_id: Session identifier (creates new if None)
            user_message: User's message/question
            repository_ids: List of repository IDs to search in
            explanation_mode: Explanation mode for response
            top_k: Number of code chunks to retrieve
            include_history: Whether to include conversation history in prompt
            
        Yields:
            Tuple[str, Optional[List[Citation]], Optional[str]]: 
                (response_chunk, citations, session_id)
                Citations and session_id are only in the first yield
            
        Requirements:
        - 6.2: Retrieve relevant Code_Chunks using semantic search
        - 6.3: Construct a prompt with code context and user question
        - 6.4: Send prompt to Ollama for inference (streaming)
        - 6.5: Return response with citations to source Code_Chunks
        - 6.6: Maintain Chat_Session history
        """
        # Get or create session
        session = await self.get_or_create_session(
            session_id,
            repository_ids,
            explanation_mode
        )
        
        # Retrieve relevant code chunks
        logger.info(f"Retrieving top {top_k} chunks for streaming query: {user_message[:100]}...")
        search_results = await self.search_service.search_hybrid(
            query=user_message,
            top_k=top_k,
            repository_ids=repository_ids,
        )
        
        # Build citations
        citations = self._build_citations(search_results)
        logger.info(f"Retrieved {len(citations)} relevant code chunks for streaming")
        
        # Calculate token budget (same as non-streaming)
        response_budget = self.max_response_tokens
        system_prompt_budget = 200
        question_budget = self._estimate_tokens(user_message) + 50
        overhead_budget = 100
        
        available_for_context = (
            self.max_context_tokens -
            response_budget -
            system_prompt_budget -
            question_budget -
            overhead_budget
        )
        
        if include_history and session.messages:
            history_budget = min(available_for_context // 3, 500)
            code_budget = available_for_context - history_budget
        else:
            history_budget = 0
            code_budget = available_for_context
        
        # Format code context
        code_context = self._format_code_context(citations, code_budget)
        
        # Format conversation history
        conversation_history = None
        if include_history and session.messages:
            conversation_history = self._truncate_conversation_history(
                session.messages,
                history_budget
            )
        
        # Build RAG prompt
        prompt = self._build_rag_prompt(
            user_question=user_message,
            code_context=code_context,
            conversation_history=conversation_history,
        )
        
        logger.debug(f"Built RAG prompt for streaming with {self._estimate_tokens(prompt)} estimated tokens")
        
        # Stream response
        logger.info("Streaming response from LLM...")
        full_response = []
        first_chunk = True
        
        async for chunk in self.llm_service.generate_stream(
            prompt=prompt,
            model=model,
            explanation_mode=explanation_mode,
            temperature=self.settings.rag_temperature,
            max_tokens=self.max_response_tokens,
        ):
            full_response.append(chunk)
            
            # Include citations and session_id only in first chunk
            if first_chunk:
                yield chunk, citations, session.session_id
                first_chunk = False
            else:
                yield chunk, None, None
        
        # Combine full response
        complete_response = "".join(full_response)
        logger.info(f"Completed streaming response with {len(complete_response)} characters")
        
        # Add messages to session history
        session.messages.append(ChatMessage(
            role="user",
            content=user_message,
            timestamp=datetime.utcnow(),
        ))
        
        session.messages.append(ChatMessage(
            role="assistant",
            content=complete_response,
            timestamp=datetime.utcnow(),
            citations=[c.to_dict() for c in citations],
        ))
        
        # Update session in Redis
        await self.update_session(session)


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_chat_service(
    redis_client: Optional[RedisClient] = None,
    llm_service: Optional[LLMService] = None,
    search_service: Optional[UnifiedSearchService] = None,
) -> ChatService:
    """
    Dependency injection for chat service.
    
    Args:
        redis_client: Redis client (uses global if not provided)
        llm_service: LLM service (creates new if not provided)
        search_service: Search service (creates new if not provided)
        
    Returns:
        ChatService: Initialized chat service instance
    """
    if redis_client is None:
        redis_client = await get_redis_client()
    
    if llm_service is None:
        llm_service = LLMService()
    
    # Note: search_service requires db session, so it should be provided
    # by the caller or created with proper dependencies
    
    return ChatService(
        redis_client=redis_client,
        llm_service=llm_service,
        search_service=search_service,
    )

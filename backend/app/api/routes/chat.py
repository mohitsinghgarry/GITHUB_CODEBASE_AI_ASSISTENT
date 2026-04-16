"""
API routes for chat operations.

This module implements RESTful endpoints for RAG-based chat with the codebase,
including streaming responses, session management, and conversation history.

Requirements:
- 6.1: Create or retrieve a Chat_Session
- 6.2: Retrieve relevant Code_Chunks using semantic search
- 6.3: Construct a prompt with code context and user question
- 6.4: Send prompt to Ollama for inference
- 6.5: Return response with citations to source Code_Chunks
- 6.6: Maintain Chat_Session history for context-aware follow-up questions
- 6.7: Summarize or truncate older messages when session exceeds token limits
- 6.8: Support streaming responses for real-time user feedback
- 10.1: Expose RESTful endpoints for chat operations
- 10.2: Validate all incoming requests and return appropriate HTTP status codes
"""

import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import RedisClient, get_redis_client
from app.database import get_db
from app.models.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionSchema,
    ChatStreamChunk,
    CitationSchema,
    ErrorResponse,
    SessionDeleteResponse,
    SessionListResponse,
)
from app.services.chat_service import ChatService, Citation
from app.services.llm_service import LLMService, OllamaConnectionError
from app.services.search_service import UnifiedSearchService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_chat_service(
    redis_client: RedisClient = Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
) -> ChatService:
    """
    Dependency injection for chat service.
    
    Args:
        redis_client: Redis client for session storage
        db: Database session
        
    Returns:
        ChatService: Initialized chat service instance
    """
    llm_service = LLMService()
    search_service = UnifiedSearchService(db=db)
    
    return ChatService(
        redis_client=redis_client,
        llm_service=llm_service,
        search_service=search_service,
    )


# ============================================================================
# Helper Functions
# ============================================================================


def citation_to_schema(citation: Citation) -> CitationSchema:
    """
    Convert Citation dataclass to CitationSchema.
    
    Args:
        citation: Citation instance
        
    Returns:
        CitationSchema: Pydantic schema instance
    """
    return CitationSchema(
        chunk_id=citation.chunk_id,
        repository_id=citation.repository_id,
        file_path=citation.file_path,
        start_line=citation.start_line,
        end_line=citation.end_line,
        language=citation.language,
        content=citation.content,
        score=citation.score,
    )


async def stream_chat_response(
    chat_service: ChatService,
    request: ChatRequest,
) -> AsyncIterator[str]:
    """
    Stream chat response as Server-Sent Events.
    
    Args:
        chat_service: Chat service instance
        request: Chat request
        
    Yields:
        str: SSE-formatted response chunks
        
    Requirement 6.8: Support streaming responses for real-time user feedback
    """
    try:
        first_chunk = True
        
        async for chunk, citations, session_id in chat_service.chat_stream(
            session_id=request.session_id,
            user_message=request.message,
            repository_ids=request.repository_ids,
            explanation_mode=request.explanation_mode,
            top_k=request.top_k,
            include_history=request.include_history,
        ):
            # Build response chunk
            if first_chunk:
                # Include citations and session_id in first chunk
                response_chunk = ChatStreamChunk(
                    chunk=chunk,
                    citations=[citation_to_schema(c) for c in citations] if citations else None,
                    session_id=session_id,
                    done=False,
                )
                first_chunk = False
            else:
                # Subsequent chunks only contain text
                response_chunk = ChatStreamChunk(
                    chunk=chunk,
                    citations=None,
                    session_id=None,
                    done=False,
                )
            
            # Format as SSE
            yield f"data: {response_chunk.model_dump_json()}\n\n"
        
        # Send final "done" chunk
        done_chunk = ChatStreamChunk(
            chunk="",
            citations=None,
            session_id=None,
            done=True,
        )
        yield f"data: {done_chunk.model_dump_json()}\n\n"
        
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error during streaming: {e}")
        error_chunk = {
            "error": "LLM service unavailable",
            "message": str(e),
            "done": True,
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
        
    except Exception as e:
        logger.error(f"Error during streaming chat: {e}", exc_info=True)
        error_chunk = {
            "error": "Internal server error",
            "message": "An unexpected error occurred during chat",
            "done": True,
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"


# ============================================================================
# API Endpoints
# ============================================================================


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description=(
        "Send a message to chat with the codebase. Retrieves relevant code chunks "
        "and generates a response using RAG. Supports both streaming and non-streaming modes."
    ),
    responses={
        200: {"description": "Chat response generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Send a chat message and get a response.
    
    This endpoint processes a user message through the RAG pipeline:
    1. Retrieves relevant code chunks using hybrid search
    2. Constructs a prompt with code context and conversation history
    3. Generates a response using Ollama
    4. Returns the response with citations to source code
    
    Supports both streaming and non-streaming modes:
    - Non-streaming (stream=false): Returns complete response
    - Streaming (stream=true): Returns Server-Sent Events stream
    
    **Validates: Requirements 6.1-6.8, 10.1, 10.2**
    """
    try:
        # Handle streaming mode
        if request.stream:
            logger.info(
                f"Processing streaming chat request for repositories {request.repository_ids}"
            )
            return StreamingResponse(
                stream_chat_response(chat_service, request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable nginx buffering
                },
            )
        
        # Handle non-streaming mode
        logger.info(
            f"Processing chat request for repositories {request.repository_ids}"
        )
        
        response, citations, session_id = await chat_service.chat(
            session_id=request.session_id,
            user_message=request.message,
            repository_ids=request.repository_ids,
            explanation_mode=request.explanation_mode,
            top_k=request.top_k,
            include_history=request.include_history,
        )
        
        logger.info(
            f"Generated chat response with {len(citations)} citations "
            f"for session {session_id}"
        )
        
        return ChatResponse(
            response=response,
            citations=[citation_to_schema(c) for c in citations],
            session_id=session_id,
        )
        
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLM service unavailable",
                "message": str(e),
                "details": [
                    {
                        "field": "ollama",
                        "message": "Unable to connect to Ollama. Please ensure it is running."
                    }
                ]
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "details": None
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing your message",
                "details": None
            }
        )


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionSchema,
    status_code=status.HTTP_200_OK,
    summary="Get chat session",
    description="Retrieve a chat session with its conversation history.",
    responses={
        200: {"description": "Session retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatSessionSchema:
    """
    Get a chat session by ID.
    
    Returns the complete session including all messages and metadata.
    
    **Validates: Requirements 6.6, 10.1**
    """
    try:
        session = await chat_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Session not found",
                    "message": f"Chat session with ID {session_id} does not exist",
                    "details": [
                        {
                            "field": "session_id",
                            "message": f"No session found with ID {session_id}"
                        }
                    ]
                }
            )
        
        logger.info(f"Retrieved session {session_id} with {len(session.messages)} messages")
        
        # Convert to schema
        from app.models.schemas.chat import ChatMessageSchema
        
        return ChatSessionSchema(
            session_id=session.session_id,
            repository_ids=session.repository_ids,
            messages=[
                ChatMessageSchema(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    citations=[
                        CitationSchema(**citation) for citation in msg.citations
                    ] if msg.citations else None,
                )
                for msg in session.messages
            ],
            explanation_mode=session.explanation_mode,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving the session",
                "details": None
            }
        )


@router.delete(
    "/sessions/{session_id}",
    response_model=SessionDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete chat session",
    description="Delete a chat session and its conversation history.",
    responses={
        200: {"description": "Session deleted successfully"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def delete_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service),
) -> SessionDeleteResponse:
    """
    Delete a chat session.
    
    Removes the session and all its conversation history from Redis.
    
    **Validates: Requirements 6.6, 10.1**
    """
    try:
        # Check if session exists
        session = await chat_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Session not found",
                    "message": f"Chat session with ID {session_id} does not exist",
                    "details": [
                        {
                            "field": "session_id",
                            "message": f"No session found with ID {session_id}"
                        }
                    ]
                }
            )
        
        # Delete session
        deleted = await chat_service.delete_session(session_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Deletion failed",
                    "message": "Failed to delete session",
                    "details": None
                }
            )
        
        logger.info(f"Deleted session {session_id}")
        
        return SessionDeleteResponse(
            message=f"Session {session_id} deleted successfully",
            deleted_session_id=session_id,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while deleting the session",
                "details": None
            }
        )


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all chat sessions",
    description="Retrieve a list of all active chat session IDs.",
    responses={
        200: {"description": "Sessions retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def list_sessions(
    chat_service: ChatService = Depends(get_chat_service),
) -> SessionListResponse:
    """
    List all active chat sessions.
    
    Returns a list of session IDs for all active sessions stored in Redis.
    
    **Validates: Requirements 6.6, 10.1**
    """
    try:
        session_ids = await chat_service.list_sessions()
        
        logger.info(f"Retrieved {len(session_ids)} active sessions")
        
        return SessionListResponse(
            sessions=session_ids,
            total=len(session_ids),
        )
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while listing sessions",
                "details": None
            }
        )

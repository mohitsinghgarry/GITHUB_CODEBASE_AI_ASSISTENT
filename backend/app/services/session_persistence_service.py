"""
Session persistence service for storing chat sessions in the database.

This service handles permanent storage of chat sessions and messages,
allowing sessions to persist across page navigations and browser restarts.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.orm.chat_session import ChatSession as ChatSessionORM, ChatMessage as ChatMessageORM

logger = logging.getLogger(__name__)


class SessionPersistenceService:
    """Service for persisting chat sessions to the database."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the session persistence service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def save_session(
        self,
        session_id: str,
        repository_ids: List[UUID],
        model: str,
        title: Optional[str] = None,
    ) -> ChatSessionORM:
        """
        Create or update a chat session in the database.
        
        Args:
            session_id: Unique session identifier
            repository_ids: List of repository IDs
            model: Model used for the session
            title: Optional session title
            
        Returns:
            ChatSessionORM: The created or updated session
        """
        # Check if session exists
        result = await self.db.execute(
            select(ChatSessionORM).where(ChatSessionORM.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            # Update existing session
            session.updated_at = datetime.utcnow()
            session.repository_ids = [str(rid) for rid in repository_ids]
            session.model = model
            if title:
                session.title = title
        else:
            # Create new session
            session = ChatSessionORM(
                id=session_id,
                repository_ids=[str(rid) for rid in repository_ids],
                model=model,
                title=title,
            )
            self.db.add(session)
        
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(f"Saved session {session_id} to database")
        return session
    
    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[dict]] = None,
    ) -> ChatMessageORM:
        """
        Save a chat message to the database.
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            citations: Optional citations array
            
        Returns:
            ChatMessageORM: The created message
        """
        message = ChatMessageORM(
            session_id=session_id,
            role=role,
            content=content,
            citations=citations,
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        # Update session's updated_at timestamp
        result = await self.db.execute(
            select(ChatSessionORM).where(ChatSessionORM.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.updated_at = datetime.utcnow()
            await self.db.commit()
        
        logger.debug(f"Saved message to session {session_id}")
        return message
    
    async def get_session(self, session_id: str) -> Optional[ChatSessionORM]:
        """
        Retrieve a session with all its messages.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ChatSessionORM or None: The session with messages, or None if not found
        """
        result = await self.db.execute(
            select(ChatSessionORM)
            .where(ChatSessionORM.id == session_id)
            .options(selectinload(ChatSessionORM.messages))
        )
        return result.scalar_one_or_none()
    
    async def list_sessions(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[ChatSessionORM], int]:
        """
        List all chat sessions ordered by most recent first.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            Tuple of (sessions list, total count)
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(ChatSessionORM)
        )
        total = count_result.scalar_one()
        
        # Get sessions with message count
        result = await self.db.execute(
            select(ChatSessionORM)
            .options(selectinload(ChatSessionORM.messages))
            .order_by(desc(ChatSessionORM.updated_at))
            .limit(limit)
            .offset(offset)
        )
        sessions = result.scalars().all()
        
        return list(sessions), total
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session was deleted, False if not found
        """
        result = await self.db.execute(
            select(ChatSessionORM).where(ChatSessionORM.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        await self.db.delete(session)
        await self.db.commit()
        
        logger.info(f"Deleted session {session_id} from database")
        return True

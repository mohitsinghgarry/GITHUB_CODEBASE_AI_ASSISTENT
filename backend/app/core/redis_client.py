"""
Redis client wrapper with connection pool management.

This module provides a Redis client wrapper with helper methods for session storage,
caching, and job status management. It includes TTL configuration for different data types
and connection pool management for efficient resource usage.

Requirements:
- 6.6: Maintain Chat_Session history for context-aware follow-up questions
- 14.2: Persist repository metadata, ingestion job status, and Chat_Session history
"""

import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper with connection pool management.
    
    This class provides a high-level interface for Redis operations with
    automatic connection pooling, error handling, and TTL management.
    
    Attributes:
        pool: Redis connection pool
        client: Redis client instance
    """
    
    def __init__(self, redis_url: Optional[str] = None, max_connections: Optional[int] = None):
        """
        Initialize Redis client with connection pool.
        
        Args:
            redis_url: Redis connection URL (defaults to settings)
            max_connections: Maximum connections in pool (defaults to settings)
        """
        settings = get_settings()
        
        self.redis_url = redis_url or settings.redis_url
        self.max_connections = max_connections or settings.redis_max_connections
        
        # TTL configuration (in seconds)
        self.session_ttl = settings.session_ttl_hours * 3600
        self.cache_ttl = settings.cache_ttl_hours * 3600
        self.job_status_ttl = 7 * 24 * 3600  # 7 days
        
        # Connection pool and client (initialized in connect())
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None
        
        logger.info(
            f"Redis client initialized with URL: {self._mask_url(self.redis_url)}, "
            f"max_connections: {self.max_connections}"
        )
    
    @staticmethod
    def _mask_url(url: str) -> str:
        """Mask sensitive information in Redis URL for logging."""
        if "@" in url:
            # Mask password in redis://user:password@host:port/db
            parts = url.split("@")
            auth_part = parts[0].split(":")
            if len(auth_part) >= 3:
                auth_part[2] = "****"
                parts[0] = ":".join(auth_part)
            return "@".join(parts)
        return url
    
    async def connect(self) -> None:
        """
        Establish connection pool to Redis.
        
        This method should be called during application startup.
        
        Raises:
            ConnectionError: If unable to connect to Redis
        """
        try:
            self.pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                decode_responses=True,
                encoding="utf-8",
            )
            self.client = Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            
            logger.info("Successfully connected to Redis")
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Unable to connect to Redis: {e}")
    
    async def disconnect(self) -> None:
        """
        Close Redis connection pool.
        
        This method should be called during application shutdown.
        """
        if self.client:
            await self.client.close()
            logger.info("Redis client closed")
        
        if self.pool:
            await self.pool.disconnect()
            logger.info("Redis connection pool closed")
    
    async def ping(self) -> bool:
        """
        Check if Redis connection is alive.
        
        Returns:
            bool: True if connection is alive, False otherwise
        """
        try:
            if self.client:
                return await self.client.ping()
            return False
        except RedisError:
            return False
    
    # ============================================================================
    # Session Storage Methods (Requirement 6.6)
    # ============================================================================
    
    async def save_session(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Save chat session data to Redis.
        
        Args:
            session_id: Unique session identifier
            session_data: Session data dictionary
            ttl: Time-to-live in seconds (defaults to session_ttl)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"session:{session_id}"
            ttl = ttl or self.session_ttl
            
            # Serialize session data to JSON
            serialized_data = json.dumps(session_data, default=str)
            
            # Store with TTL
            await self.client.setex(key, ttl, serialized_data)
            
            logger.debug(f"Saved session {session_id} with TTL {ttl}s")
            return True
        except RedisError as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve chat session data from Redis.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Optional[Dict[str, Any]]: Session data or None if not found
        """
        try:
            key = f"session:{session_id}"
            data = await self.client.get(key)
            
            if data:
                logger.debug(f"Retrieved session {session_id}")
                return json.loads(data)
            
            logger.debug(f"Session {session_id} not found")
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete chat session from Redis.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            key = f"session:{session_id}"
            result = await self.client.delete(key)
            
            logger.debug(f"Deleted session {session_id}")
            return result > 0
        except RedisError as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def update_session_ttl(self, session_id: str, ttl: Optional[int] = None) -> bool:
        """
        Update TTL for an existing session.
        
        Args:
            session_id: Unique session identifier
            ttl: New time-to-live in seconds (defaults to session_ttl)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"session:{session_id}"
            ttl = ttl or self.session_ttl
            
            result = await self.client.expire(key, ttl)
            
            if result:
                logger.debug(f"Updated TTL for session {session_id} to {ttl}s")
            return result
        except RedisError as e:
            logger.error(f"Failed to update TTL for session {session_id}: {e}")
            return False
    
    async def list_sessions(self, pattern: str = "session:*") -> List[str]:
        """
        List all session IDs matching a pattern.
        
        Args:
            pattern: Redis key pattern (default: "session:*")
            
        Returns:
            List[str]: List of session IDs (without "session:" prefix)
        """
        try:
            keys = await self.client.keys(pattern)
            # Remove "session:" prefix from keys
            session_ids = [key.replace("session:", "") for key in keys]
            
            logger.debug(f"Found {len(session_ids)} sessions")
            return session_ids
        except RedisError as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    # ============================================================================
    # Caching Methods
    # ============================================================================
    
    async def cache_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        prefix: str = "cache"
    ) -> bool:
        """
        Store a value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (defaults to cache_ttl)
            prefix: Key prefix (default: "cache")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            full_key = f"{prefix}:{key}"
            ttl = ttl or self.cache_ttl
            
            # Serialize value to JSON
            serialized_value = json.dumps(value, default=str)
            
            # Store with TTL
            await self.client.setex(full_key, ttl, serialized_value)
            
            logger.debug(f"Cached {full_key} with TTL {ttl}s")
            return True
        except RedisError as e:
            logger.error(f"Failed to cache {key}: {e}")
            return False
    
    async def cache_get(self, key: str, prefix: str = "cache") -> Optional[Any]:
        """
        Retrieve a value from cache.
        
        Args:
            key: Cache key
            prefix: Key prefix (default: "cache")
            
        Returns:
            Optional[Any]: Cached value or None if not found
        """
        try:
            full_key = f"{prefix}:{key}"
            data = await self.client.get(full_key)
            
            if data:
                logger.debug(f"Cache hit for {full_key}")
                return json.loads(data)
            
            logger.debug(f"Cache miss for {full_key}")
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get cache {key}: {e}")
            return None
    
    async def cache_delete(self, key: str, prefix: str = "cache") -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            prefix: Key prefix (default: "cache")
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            full_key = f"{prefix}:{key}"
            result = await self.client.delete(full_key)
            
            logger.debug(f"Deleted cache {full_key}")
            return result > 0
        except RedisError as e:
            logger.error(f"Failed to delete cache {key}: {e}")
            return False
    
    async def cache_exists(self, key: str, prefix: str = "cache") -> bool:
        """
        Check if a cache key exists.
        
        Args:
            key: Cache key
            prefix: Key prefix (default: "cache")
            
        Returns:
            bool: True if exists, False otherwise
        """
        try:
            full_key = f"{prefix}:{key}"
            result = await self.client.exists(full_key)
            return result > 0
        except RedisError as e:
            logger.error(f"Failed to check cache existence {key}: {e}")
            return False
    
    async def cache_clear(self, pattern: str = "cache:*") -> int:
        """
        Clear all cache entries matching a pattern.
        
        Args:
            pattern: Redis key pattern (default: "cache:*")
            
        Returns:
            int: Number of keys deleted
        """
        try:
            keys = await self.client.keys(pattern)
            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries")
                return deleted
            return 0
        except RedisError as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0
    
    # ============================================================================
    # Job Status Methods (Requirement 14.2)
    # ============================================================================
    
    async def save_job_status(
        self,
        job_id: str,
        status_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Save ingestion job status to Redis.
        
        Args:
            job_id: Unique job identifier
            status_data: Job status data dictionary
            ttl: Time-to-live in seconds (defaults to job_status_ttl)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"job:{job_id}"
            ttl = ttl or self.job_status_ttl
            
            # Serialize status data to JSON
            serialized_data = json.dumps(status_data, default=str)
            
            # Store with TTL
            await self.client.setex(key, ttl, serialized_data)
            
            logger.debug(f"Saved job status {job_id} with TTL {ttl}s")
            return True
        except RedisError as e:
            logger.error(f"Failed to save job status {job_id}: {e}")
            return False
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve ingestion job status from Redis.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Optional[Dict[str, Any]]: Job status data or None if not found
        """
        try:
            key = f"job:{job_id}"
            data = await self.client.get(key)
            
            if data:
                logger.debug(f"Retrieved job status {job_id}")
                return json.loads(data)
            
            logger.debug(f"Job status {job_id} not found")
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get job status {job_id}: {e}")
            return None
    
    async def update_job_progress(
        self,
        job_id: str,
        progress: int,
        stage: Optional[str] = None
    ) -> bool:
        """
        Update job progress percentage and optionally stage.
        
        Args:
            job_id: Unique job identifier
            progress: Progress percentage (0-100)
            stage: Current stage name (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get existing job status
            job_status = await self.get_job_status(job_id)
            if not job_status:
                logger.warning(f"Job {job_id} not found, cannot update progress")
                return False
            
            # Update progress and stage
            job_status["progress"] = progress
            if stage:
                job_status["stage"] = stage
            
            # Save updated status
            return await self.save_job_status(job_id, job_status)
        except Exception as e:
            logger.error(f"Failed to update job progress {job_id}: {e}")
            return False
    
    async def delete_job_status(self, job_id: str) -> bool:
        """
        Delete job status from Redis.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            key = f"job:{job_id}"
            result = await self.client.delete(key)
            
            logger.debug(f"Deleted job status {job_id}")
            return result > 0
        except RedisError as e:
            logger.error(f"Failed to delete job status {job_id}: {e}")
            return False
    
    # ============================================================================
    # Generic Key-Value Methods
    # ============================================================================
    
    async def set(
        self,
        key: str,
        value: Union[str, int, float, Dict, List],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a key-value pair with optional TTL.
        
        Args:
            key: Redis key
            value: Value to store
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Serialize complex types to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
            
            return True
        except RedisError as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: Redis key
            
        Returns:
            Optional[Any]: Value or None if not found
        """
        try:
            value = await self.client.get(key)
            
            if value:
                # Try to parse as JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            
            return None
        except RedisError as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.
        
        Args:
            *keys: Redis keys to delete
            
        Returns:
            int: Number of keys deleted
        """
        try:
            if keys:
                return await self.client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Failed to delete keys: {e}")
            return 0
    
    async def exists(self, *keys: str) -> int:
        """
        Check if one or more keys exist.
        
        Args:
            *keys: Redis keys to check
            
        Returns:
            int: Number of keys that exist
        """
        try:
            if keys:
                return await self.client.exists(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Failed to check key existence: {e}")
            return 0
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set TTL for an existing key.
        
        Args:
            key: Redis key
            ttl: Time-to-live in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return await self.client.expire(key, ttl)
        except RedisError as e:
            logger.error(f"Failed to set TTL for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key.
        
        Args:
            key: Redis key
            
        Returns:
            int: Remaining TTL in seconds (-1 if no TTL, -2 if key doesn't exist)
        """
        try:
            return await self.client.ttl(key)
        except RedisError as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return -2
    
    # ============================================================================
    # Hash Methods (for structured data)
    # ============================================================================
    
    async def hset(self, key: str, field: str, value: Any) -> bool:
        """
        Set a field in a hash.
        
        Args:
            key: Redis hash key
            field: Field name
            value: Field value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            
            await self.client.hset(key, field, value)
            return True
        except RedisError as e:
            logger.error(f"Failed to set hash field {key}.{field}: {e}")
            return False
    
    async def hget(self, key: str, field: str) -> Optional[Any]:
        """
        Get a field from a hash.
        
        Args:
            key: Redis hash key
            field: Field name
            
        Returns:
            Optional[Any]: Field value or None if not found
        """
        try:
            value = await self.client.hget(key, field)
            
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            
            return None
        except RedisError as e:
            logger.error(f"Failed to get hash field {key}.{field}: {e}")
            return None
    
    async def hgetall(self, key: str) -> Dict[str, Any]:
        """
        Get all fields from a hash.
        
        Args:
            key: Redis hash key
            
        Returns:
            Dict[str, Any]: Dictionary of field-value pairs
        """
        try:
            data = await self.client.hgetall(key)
            
            # Try to parse JSON values
            result = {}
            for field, value in data.items():
                try:
                    result[field] = json.loads(value)
                except json.JSONDecodeError:
                    result[field] = value
            
            return result
        except RedisError as e:
            logger.error(f"Failed to get all hash fields {key}: {e}")
            return {}
    
    async def hdel(self, key: str, *fields: str) -> int:
        """
        Delete one or more fields from a hash.
        
        Args:
            key: Redis hash key
            *fields: Field names to delete
            
        Returns:
            int: Number of fields deleted
        """
        try:
            if fields:
                return await self.client.hdel(key, *fields)
            return 0
        except RedisError as e:
            logger.error(f"Failed to delete hash fields {key}: {e}")
            return 0


# ============================================================================
# Global Redis Client Instance
# ============================================================================

# Singleton Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """
    Get the global Redis client instance.
    
    This function returns the singleton Redis client instance.
    The client must be initialized with connect() before use.
    
    Returns:
        RedisClient: The global Redis client instance
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client


async def close_redis_client() -> None:
    """
    Close the global Redis client instance.
    
    This function should be called during application shutdown.
    """
    global _redis_client
    if _redis_client is not None:
        await _redis_client.disconnect()
        _redis_client = None


# Aliases for consistency with database module
async def init_redis() -> None:
    """
    Initialize the global Redis client instance.
    
    This function should be called during application startup.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()


async def close_redis() -> None:
    """
    Close the global Redis client instance.
    
    Alias for close_redis_client() for consistency with database module.
    """
    await close_redis_client()

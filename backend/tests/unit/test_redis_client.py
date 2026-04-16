"""
Unit tests for Redis client wrapper.

Tests connection management, session storage, caching, and job status operations.

**Validates: Requirements 14.2**
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.core.redis_client import RedisClient


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.redis_url = "redis://localhost:6379/0"
    settings.redis_max_connections = 50
    settings.session_ttl_hours = 24
    settings.cache_ttl_hours = 1
    return settings


@pytest.fixture
def redis_client(mock_settings):
    """Create a Redis client instance for testing."""
    with patch("app.core.redis_client.get_settings", return_value=mock_settings):
        client = RedisClient()
        return client


# ============================================================================
# Connection Management Tests
# ============================================================================


@pytest.mark.asyncio
async def test_connect_success(redis_client):
    """Test successful Redis connection."""
    mock_pool = MagicMock()
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    
    with patch("app.core.redis_client.ConnectionPool.from_url", return_value=mock_pool):
        with patch("app.core.redis_client.Redis", return_value=mock_redis):
            await redis_client.connect()
            
            assert redis_client.pool == mock_pool
            assert redis_client.client == mock_redis
            mock_redis.ping.assert_called_once()


@pytest.mark.asyncio
async def test_connect_failure(redis_client):
    """Test Redis connection failure."""
    with patch("app.core.redis_client.ConnectionPool.from_url", side_effect=ConnectionError("Connection failed")):
        with pytest.raises(ConnectionError) as exc_info:
            await redis_client.connect()
        
        assert "Unable to connect to Redis" in str(exc_info.value)


@pytest.mark.asyncio
async def test_connect_timeout(redis_client):
    """Test Redis connection timeout."""
    with patch("app.core.redis_client.ConnectionPool.from_url", side_effect=TimeoutError("Connection timeout")):
        with pytest.raises(ConnectionError) as exc_info:
            await redis_client.connect()
        
        assert "Unable to connect to Redis" in str(exc_info.value)


@pytest.mark.asyncio
async def test_disconnect(redis_client):
    """Test Redis disconnection."""
    mock_client = AsyncMock()
    mock_pool = AsyncMock()
    
    redis_client.client = mock_client
    redis_client.pool = mock_pool
    
    await redis_client.disconnect()
    
    mock_client.close.assert_called_once()
    mock_pool.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_with_none_client(redis_client):
    """Test disconnection when client is None."""
    redis_client.client = None
    redis_client.pool = None
    
    # Should not raise an error
    await redis_client.disconnect()


@pytest.mark.asyncio
async def test_ping_success(redis_client):
    """Test successful ping."""
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    redis_client.client = mock_client
    
    result = await redis_client.ping()
    
    assert result is True
    mock_client.ping.assert_called_once()


@pytest.mark.asyncio
async def test_ping_failure(redis_client):
    """Test ping failure."""
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(side_effect=RedisError("Connection lost"))
    redis_client.client = mock_client
    
    result = await redis_client.ping()
    
    assert result is False


@pytest.mark.asyncio
async def test_ping_no_client(redis_client):
    """Test ping when client is None."""
    redis_client.client = None
    
    result = await redis_client.ping()
    
    assert result is False


# ============================================================================
# Session Storage Tests
# ============================================================================


@pytest.mark.asyncio
async def test_save_session(redis_client):
    """Test saving session data."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    session_id = "test-session-123"
    session_data = {
        "session_id": session_id,
        "messages": [{"role": "user", "content": "Hello"}],
        "repository_ids": ["repo-1"]
    }
    
    result = await redis_client.save_session(session_id, session_data)
    
    assert result is True
    mock_client.setex.assert_called_once()
    
    # Verify the key format
    call_args = mock_client.setex.call_args
    assert call_args[0][0] == f"session:{session_id}"
    assert call_args[0][1] == redis_client.session_ttl
    
    # Verify data is JSON serialized
    stored_data = json.loads(call_args[0][2])
    assert stored_data == session_data


@pytest.mark.asyncio
async def test_save_session_with_custom_ttl(redis_client):
    """Test saving session with custom TTL."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    session_id = "test-session-123"
    session_data = {"test": "data"}
    custom_ttl = 3600
    
    result = await redis_client.save_session(session_id, session_data, ttl=custom_ttl)
    
    assert result is True
    call_args = mock_client.setex.call_args
    assert call_args[0][1] == custom_ttl


@pytest.mark.asyncio
async def test_save_session_error(redis_client):
    """Test save session error handling."""
    mock_client = AsyncMock()
    mock_client.setex = AsyncMock(side_effect=RedisError("Write failed"))
    redis_client.client = mock_client
    
    result = await redis_client.save_session("test", {"data": "test"})
    
    assert result is False


@pytest.mark.asyncio
async def test_get_session(redis_client):
    """Test retrieving session data."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    session_id = "test-session-123"
    session_data = {
        "session_id": session_id,
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    mock_client.get = AsyncMock(return_value=json.dumps(session_data))
    
    result = await redis_client.get_session(session_id)
    
    assert result == session_data
    mock_client.get.assert_called_once_with(f"session:{session_id}")


@pytest.mark.asyncio
async def test_get_session_not_found(redis_client):
    """Test retrieving non-existent session."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.get = AsyncMock(return_value=None)
    
    result = await redis_client.get_session("non-existent")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_session_error(redis_client):
    """Test get session error handling."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=RedisError("Read failed"))
    redis_client.client = mock_client
    
    result = await redis_client.get_session("test")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_session_invalid_json(redis_client):
    """Test get session with invalid JSON."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value="invalid json{")
    redis_client.client = mock_client
    
    result = await redis_client.get_session("test")
    
    assert result is None


@pytest.mark.asyncio
async def test_delete_session(redis_client):
    """Test deleting session."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.delete = AsyncMock(return_value=1)
    
    session_id = "test-session-123"
    result = await redis_client.delete_session(session_id)
    
    assert result is True
    mock_client.delete.assert_called_once_with(f"session:{session_id}")


@pytest.mark.asyncio
async def test_delete_session_not_found(redis_client):
    """Test deleting non-existent session."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.delete = AsyncMock(return_value=0)
    
    result = await redis_client.delete_session("non-existent")
    
    assert result is False


@pytest.mark.asyncio
async def test_delete_session_error(redis_client):
    """Test delete session error handling."""
    mock_client = AsyncMock()
    mock_client.delete = AsyncMock(side_effect=RedisError("Delete failed"))
    redis_client.client = mock_client
    
    result = await redis_client.delete_session("test")
    
    assert result is False


@pytest.mark.asyncio
async def test_update_session_ttl(redis_client):
    """Test updating session TTL."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.expire = AsyncMock(return_value=True)
    
    session_id = "test-session-123"
    result = await redis_client.update_session_ttl(session_id)
    
    assert result is True
    mock_client.expire.assert_called_once_with(
        f"session:{session_id}",
        redis_client.session_ttl
    )


@pytest.mark.asyncio
async def test_update_session_ttl_custom(redis_client):
    """Test updating session TTL with custom value."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.expire = AsyncMock(return_value=True)
    
    custom_ttl = 7200
    result = await redis_client.update_session_ttl("test", ttl=custom_ttl)
    
    assert result is True
    call_args = mock_client.expire.call_args
    assert call_args[0][1] == custom_ttl


@pytest.mark.asyncio
async def test_list_sessions(redis_client):
    """Test listing sessions."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.keys = AsyncMock(return_value=[
        "session:test-1",
        "session:test-2",
        "session:test-3"
    ])
    
    result = await redis_client.list_sessions()
    
    assert len(result) == 3
    assert "test-1" in result
    assert "test-2" in result
    assert "test-3" in result


@pytest.mark.asyncio
async def test_list_sessions_empty(redis_client):
    """Test listing sessions when none exist."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.keys = AsyncMock(return_value=[])
    
    result = await redis_client.list_sessions()
    
    assert result == []


# ============================================================================
# Caching Tests
# ============================================================================


@pytest.mark.asyncio
async def test_cache_set(redis_client):
    """Test setting cache value."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    key = "search:query-hash:repo-1"
    value = {"results": [{"file": "test.py", "score": 0.95}]}
    
    result = await redis_client.cache_set(key, value)
    
    assert result is True
    mock_client.setex.assert_called_once()
    
    # Verify the key format
    call_args = mock_client.setex.call_args
    assert call_args[0][0] == f"cache:{key}"
    assert call_args[0][1] == redis_client.cache_ttl


@pytest.mark.asyncio
async def test_cache_set_custom_prefix(redis_client):
    """Test setting cache with custom prefix."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    result = await redis_client.cache_set("key", "value", prefix="custom")
    
    assert result is True
    call_args = mock_client.setex.call_args
    assert call_args[0][0] == "custom:key"


@pytest.mark.asyncio
async def test_cache_set_error(redis_client):
    """Test cache set error handling."""
    mock_client = AsyncMock()
    mock_client.setex = AsyncMock(side_effect=RedisError("Write failed"))
    redis_client.client = mock_client
    
    result = await redis_client.cache_set("key", "value")
    
    assert result is False


@pytest.mark.asyncio
async def test_cache_get(redis_client):
    """Test getting cache value."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    key = "search:query-hash:repo-1"
    value = {"results": [{"file": "test.py", "score": 0.95}]}
    
    mock_client.get = AsyncMock(return_value=json.dumps(value))
    
    result = await redis_client.cache_get(key)
    
    assert result == value
    mock_client.get.assert_called_once_with(f"cache:{key}")


@pytest.mark.asyncio
async def test_cache_get_not_found(redis_client):
    """Test cache miss."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.get = AsyncMock(return_value=None)
    
    result = await redis_client.cache_get("non-existent")
    
    assert result is None


@pytest.mark.asyncio
async def test_cache_delete(redis_client):
    """Test deleting cache value."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.delete = AsyncMock(return_value=1)
    
    key = "search:query-hash:repo-1"
    result = await redis_client.cache_delete(key)
    
    assert result is True
    mock_client.delete.assert_called_once_with(f"cache:{key}")


@pytest.mark.asyncio
async def test_cache_exists(redis_client):
    """Test checking cache existence."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.exists = AsyncMock(return_value=1)
    
    result = await redis_client.cache_exists("test-key")
    
    assert result is True


@pytest.mark.asyncio
async def test_cache_exists_not_found(redis_client):
    """Test checking non-existent cache."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.exists = AsyncMock(return_value=0)
    
    result = await redis_client.cache_exists("non-existent")
    
    assert result is False


@pytest.mark.asyncio
async def test_cache_clear(redis_client):
    """Test clearing cache."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.keys = AsyncMock(return_value=["cache:key1", "cache:key2"])
    mock_client.delete = AsyncMock(return_value=2)
    
    result = await redis_client.cache_clear()
    
    assert result == 2
    mock_client.delete.assert_called_once_with("cache:key1", "cache:key2")


@pytest.mark.asyncio
async def test_cache_clear_empty(redis_client):
    """Test clearing cache when empty."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.keys = AsyncMock(return_value=[])
    
    result = await redis_client.cache_clear()
    
    assert result == 0


# ============================================================================
# Job Status Tests
# ============================================================================


@pytest.mark.asyncio
async def test_save_job_status(redis_client):
    """Test saving job status."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    job_id = "job-123"
    status_data = {
        "status": "running",
        "stage": "embedding",
        "progress": 65
    }
    
    result = await redis_client.save_job_status(job_id, status_data)
    
    assert result is True
    mock_client.setex.assert_called_once()
    
    # Verify the key format
    call_args = mock_client.setex.call_args
    assert call_args[0][0] == f"job:{job_id}"
    assert call_args[0][1] == redis_client.job_status_ttl


@pytest.mark.asyncio
async def test_save_job_status_error(redis_client):
    """Test save job status error handling."""
    mock_client = AsyncMock()
    mock_client.setex = AsyncMock(side_effect=RedisError("Write failed"))
    redis_client.client = mock_client
    
    result = await redis_client.save_job_status("job-123", {"status": "running"})
    
    assert result is False


@pytest.mark.asyncio
async def test_get_job_status(redis_client):
    """Test retrieving job status."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    job_id = "job-123"
    status_data = {
        "status": "running",
        "stage": "embedding",
        "progress": 65
    }
    
    mock_client.get = AsyncMock(return_value=json.dumps(status_data))
    
    result = await redis_client.get_job_status(job_id)
    
    assert result == status_data
    mock_client.get.assert_called_once_with(f"job:{job_id}")


@pytest.mark.asyncio
async def test_get_job_status_not_found(redis_client):
    """Test retrieving non-existent job status."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.get = AsyncMock(return_value=None)
    
    result = await redis_client.get_job_status("non-existent")
    
    assert result is None


@pytest.mark.asyncio
async def test_update_job_progress(redis_client):
    """Test updating job progress."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    job_id = "job-123"
    existing_status = {
        "status": "running",
        "stage": "chunking",
        "progress": 50
    }
    
    mock_client.get = AsyncMock(return_value=json.dumps(existing_status))
    mock_client.setex = AsyncMock()
    
    result = await redis_client.update_job_progress(job_id, 75, "embedding")
    
    assert result is True
    
    # Verify the updated data
    call_args = mock_client.setex.call_args
    updated_data = json.loads(call_args[0][2])
    assert updated_data["progress"] == 75
    assert updated_data["stage"] == "embedding"


@pytest.mark.asyncio
async def test_update_job_progress_not_found(redis_client):
    """Test updating progress for non-existent job."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.get = AsyncMock(return_value=None)
    
    result = await redis_client.update_job_progress("non-existent", 50)
    
    assert result is False


@pytest.mark.asyncio
async def test_delete_job_status(redis_client):
    """Test deleting job status."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.delete = AsyncMock(return_value=1)
    
    result = await redis_client.delete_job_status("job-123")
    
    assert result is True


# ============================================================================
# Generic Key-Value Tests
# ============================================================================


@pytest.mark.asyncio
async def test_set_and_get(redis_client):
    """Test generic set and get operations."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    key = "test:key"
    value = {"data": "test"}
    
    # Test set
    await redis_client.set(key, value, ttl=3600)
    mock_client.setex.assert_called_once_with(key, 3600, json.dumps(value, default=str))
    
    # Test get
    mock_client.get = AsyncMock(return_value=json.dumps(value))
    result = await redis_client.get(key)
    
    assert result == value


@pytest.mark.asyncio
async def test_set_without_ttl(redis_client):
    """Test set without TTL."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    await redis_client.set("key", "value")
    
    mock_client.set.assert_called_once_with("key", "value")


@pytest.mark.asyncio
async def test_set_string_value(redis_client):
    """Test set with string value."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    await redis_client.set("key", "string_value", ttl=100)
    
    mock_client.setex.assert_called_once_with("key", 100, "string_value")


@pytest.mark.asyncio
async def test_get_string_value(redis_client):
    """Test get with non-JSON string value."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.get = AsyncMock(return_value="plain string")
    
    result = await redis_client.get("key")
    
    assert result == "plain string"


@pytest.mark.asyncio
async def test_delete_multiple_keys(redis_client):
    """Test deleting multiple keys."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.delete = AsyncMock(return_value=3)
    
    result = await redis_client.delete("key1", "key2", "key3")
    
    assert result == 3
    mock_client.delete.assert_called_once_with("key1", "key2", "key3")


@pytest.mark.asyncio
async def test_exists_multiple_keys(redis_client):
    """Test checking existence of multiple keys."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.exists = AsyncMock(return_value=2)
    
    result = await redis_client.exists("key1", "key2", "key3")
    
    assert result == 2


@pytest.mark.asyncio
async def test_expire(redis_client):
    """Test setting TTL on existing key."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.expire = AsyncMock(return_value=True)
    
    result = await redis_client.expire("key", 3600)
    
    assert result is True


@pytest.mark.asyncio
async def test_ttl(redis_client):
    """Test getting TTL for a key."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.ttl = AsyncMock(return_value=3600)
    
    result = await redis_client.ttl("key")
    
    assert result == 3600


@pytest.mark.asyncio
async def test_ttl_no_expiry(redis_client):
    """Test getting TTL for key with no expiry."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.ttl = AsyncMock(return_value=-1)
    
    result = await redis_client.ttl("key")
    
    assert result == -1


@pytest.mark.asyncio
async def test_ttl_not_found(redis_client):
    """Test getting TTL for non-existent key."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.ttl = AsyncMock(return_value=-2)
    
    result = await redis_client.ttl("non-existent")
    
    assert result == -2


# ============================================================================
# Hash Operations Tests
# ============================================================================


@pytest.mark.asyncio
async def test_hash_operations(redis_client):
    """Test hash set and get operations."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    key = "repo:metadata"
    field = "name"
    value = "test-repo"
    
    # Test hset
    await redis_client.hset(key, field, value)
    mock_client.hset.assert_called_once_with(key, field, value)
    
    # Test hget
    mock_client.hget = AsyncMock(return_value=value)
    result = await redis_client.hget(key, field)
    
    assert result == value
    mock_client.hget.assert_called_once_with(key, field)


@pytest.mark.asyncio
async def test_hset_complex_value(redis_client):
    """Test hset with complex value."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    value = {"nested": "data"}
    await redis_client.hset("key", "field", value)
    
    call_args = mock_client.hset.call_args
    assert call_args[0][2] == json.dumps(value, default=str)


@pytest.mark.asyncio
async def test_hgetall(redis_client):
    """Test getting all hash fields."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    
    hash_data = {
        "field1": "value1",
        "field2": json.dumps({"nested": "data"})
    }
    mock_client.hgetall = AsyncMock(return_value=hash_data)
    
    result = await redis_client.hgetall("key")
    
    assert result["field1"] == "value1"
    assert result["field2"] == {"nested": "data"}


@pytest.mark.asyncio
async def test_hdel(redis_client):
    """Test deleting hash fields."""
    mock_client = AsyncMock()
    redis_client.client = mock_client
    mock_client.hdel = AsyncMock(return_value=2)
    
    result = await redis_client.hdel("key", "field1", "field2")
    
    assert result == 2
    mock_client.hdel.assert_called_once_with("key", "field1", "field2")


# ============================================================================
# Utility Tests
# ============================================================================


@pytest.mark.asyncio
async def test_mask_url():
    """Test URL masking for logging."""
    url_with_password = "redis://user:password123@localhost:6379/0"
    masked = RedisClient._mask_url(url_with_password)
    
    assert "password123" not in masked
    assert "****" in masked
    
    url_without_password = "redis://localhost:6379/0"
    masked = RedisClient._mask_url(url_without_password)
    
    assert masked == url_without_password


def test_redis_client_initialization(mock_settings):
    """Test Redis client initialization."""
    with patch("app.core.redis_client.get_settings", return_value=mock_settings):
        client = RedisClient()
        
        assert client.redis_url == mock_settings.redis_url
        assert client.max_connections == mock_settings.redis_max_connections
        assert client.session_ttl == mock_settings.session_ttl_hours * 3600
        assert client.cache_ttl == mock_settings.cache_ttl_hours * 3600
        assert client.job_status_ttl == 7 * 24 * 3600


def test_redis_client_custom_initialization():
    """Test Redis client with custom parameters."""
    custom_url = "redis://custom:6379/1"
    custom_max_conn = 100
    
    with patch("app.core.redis_client.get_settings"):
        client = RedisClient(redis_url=custom_url, max_connections=custom_max_conn)
        
        assert client.redis_url == custom_url
        assert client.max_connections == custom_max_conn

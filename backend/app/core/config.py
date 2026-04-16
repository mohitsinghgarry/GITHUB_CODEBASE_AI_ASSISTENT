"""
Configuration management using Pydantic Settings.

This module provides centralized configuration management for the GitHub Codebase RAG Assistant.
All configuration is loaded from environment variables with validation and type checking.

Requirements:
- 13.1: Load configuration from environment variables and configuration files
- 13.2: Support configuration for embedding model selection, chunk size, and overlap
- 13.3: Support configuration for Ollama endpoint, model name, and timeout settings
- 13.4: Support configuration for vector database connection parameters
- 13.5: Support configuration for authentication secrets and API keys
- 13.8: Validate configuration values against expected types and ranges
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are validated on initialization. Invalid values will raise
    a ValidationError with descriptive messages.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ============================================================================
    # Application Settings
    # ============================================================================
    
    app_name: str = Field(
        default="GitHub Codebase RAG Assistant",
        description="Application name"
    )
    
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # ============================================================================
    # API Settings
    # ============================================================================
    
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API v1 route prefix"
    )
    
    backend_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # ============================================================================
    # Database Settings (Requirement 13.4)
    # ============================================================================
    
    database_url: str = Field(
        ...,  # Required field
        description="PostgreSQL database URL (asyncpg driver required)",
        examples=["postgresql+asyncpg://user:pass@localhost:5432/dbname"]
    )
    
    database_pool_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum overflow connections beyond pool size"
    )
    
    # ============================================================================
    # Redis Settings (Requirement 13.4)
    # ============================================================================
    
    redis_url: str = Field(
        ...,  # Required field
        description="Redis connection URL",
        examples=["redis://localhost:6379/0"]
    )
    
    redis_max_connections: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum Redis connection pool size"
    )
    
    # ============================================================================
    # Celery Settings
    # ============================================================================
    
    celery_broker_url: str = Field(
        ...,  # Required field
        description="Celery broker URL (Redis)",
        examples=["redis://localhost:6379/1"]
    )
    
    celery_result_backend: str = Field(
        ...,  # Required field
        description="Celery result backend URL (Redis)",
        examples=["redis://localhost:6379/2"]
    )
    
    # ============================================================================
    # Ollama Settings (Requirement 13.3)
    # ============================================================================
    
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    
    ollama_model: str = Field(
        default="codellama:7b",
        description="Default Ollama model name",
        examples=["codellama:7b", "deepseek-coder:6.7b", "llama2:13b"]
    )
    
    ollama_timeout: int = Field(
        default=120,
        ge=10,
        le=600,
        description="Ollama request timeout in seconds"
    )
    
    ollama_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for Ollama requests"
    )
    
    # ============================================================================
    # Embedding Settings (Requirement 13.2)
    # ============================================================================
    
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformers model name",
        examples=[
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "BAAI/bge-small-en-v1.5"
        ]
    )
    
    embedding_dimension: int = Field(
        default=384,
        ge=128,
        le=1536,
        description="Embedding vector dimension"
    )
    
    embedding_batch_size: int = Field(
        default=32,
        ge=1,
        le=256,
        description="Batch size for embedding generation"
    )
    
    embedding_device: str = Field(
        default="cpu",
        description="Device for embedding model (cpu, cuda, mps)"
    )
    
    # ============================================================================
    # Chunking Settings (Requirement 13.2)
    # ============================================================================
    
    chunk_size: int = Field(
        default=512,
        ge=128,
        le=2048,
        description="Default chunk size in characters"
    )
    
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=512,
        description="Overlap between chunks in characters"
    )
    
    max_chunk_size: int = Field(
        default=1024,
        ge=256,
        le=4096,
        description="Maximum allowed chunk size"
    )
    
    # ============================================================================
    # Search Settings
    # ============================================================================
    
    default_top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Default number of results to return"
    )
    
    max_top_k: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum allowed top-K value"
    )
    
    hybrid_search_alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Weight for hybrid search (0=BM25 only, 1=vector only)"
    )
    
    # ============================================================================
    # RAG Settings
    # ============================================================================
    
    max_context_tokens: int = Field(
        default=4096,
        ge=512,
        le=32768,
        description="Maximum context window size in tokens"
    )
    
    max_response_tokens: int = Field(
        default=2048,
        ge=128,
        le=8192,
        description="Maximum response length in tokens"
    )
    
    rag_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM generation"
    )
    
    # ============================================================================
    # Session Settings
    # ============================================================================
    
    session_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=168,  # 1 week
        description="Session time-to-live in hours"
    )
    
    cache_ttl_hours: int = Field(
        default=1,
        ge=0,
        le=24,
        description="Cache time-to-live in hours"
    )
    
    # ============================================================================
    # Storage Settings
    # ============================================================================
    
    repo_storage_path: Path = Field(
        default=Path("./data/repositories"),
        description="Path for storing cloned repositories"
    )
    
    faiss_index_path: Path = Field(
        default=Path("./data/indices"),
        description="Path for storing FAISS indices"
    )
    
    # ============================================================================
    # Rate Limiting Settings
    # ============================================================================
    
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Maximum requests per minute per client"
    )
    
    rate_limit_burst: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Burst allowance for rate limiting"
    )
    
    # ============================================================================
    # Security Settings (Requirement 13.5)
    # ============================================================================
    
    secret_key: str = Field(
        ...,  # Required field
        min_length=32,
        description="Secret key for JWT token signing (min 32 characters)"
    )
    
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        ge=5,
        le=1440,  # 24 hours
        description="Access token expiration time in minutes"
    )
    
    # ============================================================================
    # Retry Settings (Requirements 9.5, 15.1, 15.2)
    # ============================================================================
    
    retry_max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for external service calls"
    )
    
    retry_initial_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Initial delay in seconds before first retry"
    )
    
    retry_max_delay: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="Maximum delay in seconds between retries"
    )
    
    retry_exponential_base: float = Field(
        default=2.0,
        ge=1.1,
        le=10.0,
        description="Base for exponential backoff calculation"
    )
    
    retry_jitter: bool = Field(
        default=True,
        description="Add random jitter to retry delays"
    )
    
    # ============================================================================
    # Circuit Breaker Settings (Requirement 15.6)
    # ============================================================================
    
    circuit_breaker_failure_threshold: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of failures before opening circuit breaker"
    )
    
    circuit_breaker_success_threshold: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Number of successes in half-open state to close circuit"
    )
    
    circuit_breaker_timeout: float = Field(
        default=60.0,
        ge=1.0,
        le=600.0,
        description="Seconds to wait before transitioning from open to half-open"
    )
    
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker pattern for external services"
    )
    
    # ============================================================================
    # Monitoring Settings
    # ============================================================================
    
    enable_metrics: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    
    metrics_port: int = Field(
        default=9090,
        ge=1024,
        le=65535,
        description="Port for Prometheus metrics endpoint"
    )
    
    # ============================================================================
    # Validators (Requirement 13.8)
    # ============================================================================
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(
                f"log_level must be one of {allowed_levels}, got '{v}'"
            )
        return v_upper
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed_envs = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in allowed_envs:
            raise ValueError(
                f"environment must be one of {allowed_envs}, got '{v}'"
            )
        return v_lower
    
    @field_validator("embedding_device")
    @classmethod
    def validate_embedding_device(cls, v: str) -> str:
        """Validate embedding device is one of the allowed values."""
        allowed_devices = {"cpu", "cuda", "mps"}
        v_lower = v.lower()
        if v_lower not in allowed_devices:
            raise ValueError(
                f"embedding_device must be one of {allowed_devices}, got '{v}'"
            )
        return v_lower
    
    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                # Try to parse as JSON array
                return json.loads(v)
            except json.JSONDecodeError:
                # Fall back to comma-separated values
                return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        else:
            raise ValueError(
                f"backend_cors_origins must be a list or JSON string, got {type(v)}"
            )
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "database_url must use asyncpg driver (postgresql+asyncpg://...)"
            )
        return v
    
    @field_validator("redis_url", "celery_broker_url", "celery_result_backend")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v.startswith("redis://"):
            raise ValueError(
                f"Redis URL must start with 'redis://', got '{v}'"
            )
        return v
    
    @field_validator("ollama_base_url")
    @classmethod
    def validate_ollama_url(cls, v: str) -> str:
        """Validate Ollama URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError(
                f"ollama_base_url must start with 'http://' or 'https://', got '{v}'"
            )
        return v.rstrip("/")  # Remove trailing slash
    
    @field_validator("repo_storage_path", "faiss_index_path")
    @classmethod
    def validate_storage_path(cls, v: Path) -> Path:
        """Ensure storage paths are absolute and create if they don't exist."""
        # Convert to absolute path
        abs_path = v.resolve()
        
        # Create directory if it doesn't exist
        abs_path.mkdir(parents=True, exist_ok=True)
        
        return abs_path
    
    @model_validator(mode="after")
    def validate_chunk_overlap(self) -> "Settings":
        """Validate chunk overlap is less than chunk size."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than "
                f"chunk_size ({self.chunk_size})"
            )
        return self
    
    @model_validator(mode="after")
    def validate_chunk_size_limits(self) -> "Settings":
        """Validate chunk size is within max chunk size."""
        if self.chunk_size > self.max_chunk_size:
            raise ValueError(
                f"chunk_size ({self.chunk_size}) must not exceed "
                f"max_chunk_size ({self.max_chunk_size})"
            )
        return self
    
    @model_validator(mode="after")
    def validate_top_k_limits(self) -> "Settings":
        """Validate default top-K is within max top-K."""
        if self.default_top_k > self.max_top_k:
            raise ValueError(
                f"default_top_k ({self.default_top_k}) must not exceed "
                f"max_top_k ({self.max_top_k})"
            )
        return self
    
    @model_validator(mode="after")
    def validate_token_limits(self) -> "Settings":
        """Validate response tokens don't exceed context tokens."""
        if self.max_response_tokens > self.max_context_tokens:
            raise ValueError(
                f"max_response_tokens ({self.max_response_tokens}) must not exceed "
                f"max_context_tokens ({self.max_context_tokens})"
            )
        return self
    
    @model_validator(mode="after")
    def validate_retry_delays(self) -> "Settings":
        """Validate retry max delay is greater than or equal to initial delay."""
        if self.retry_max_delay < self.retry_initial_delay:
            raise ValueError(
                f"retry_max_delay ({self.retry_max_delay}) must be >= "
                f"retry_initial_delay ({self.retry_initial_delay})"
            )
        return self
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration dictionary."""
        return {
            "url": self.redis_url,
            "max_connections": self.redis_max_connections,
        }
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration dictionary."""
        return {
            "base_url": self.ollama_base_url,
            "model": self.ollama_model,
            "timeout": self.ollama_timeout,
            "max_retries": self.ollama_max_retries,
        }
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration dictionary."""
        return {
            "model": self.embedding_model,
            "dimension": self.embedding_dimension,
            "batch_size": self.embedding_batch_size,
            "device": self.embedding_device,
        }
    
    def get_chunking_config(self) -> Dict[str, Any]:
        """Get chunking configuration dictionary."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_chunk_size": self.max_chunk_size,
        }
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration dictionary."""
        return {
            "default_top_k": self.default_top_k,
            "max_top_k": self.max_top_k,
            "hybrid_search_alpha": self.hybrid_search_alpha,
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG configuration dictionary."""
        return {
            "max_context_tokens": self.max_context_tokens,
            "max_response_tokens": self.max_response_tokens,
            "temperature": self.rag_temperature,
        }
    
    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration dictionary."""
        return {
            "max_attempts": self.retry_max_attempts,
            "initial_delay": self.retry_initial_delay,
            "max_delay": self.retry_max_delay,
            "exponential_base": self.retry_exponential_base,
            "jitter": self.retry_jitter,
        }
    
    def get_circuit_breaker_config(self) -> Dict[str, Any]:
        """Get circuit breaker configuration dictionary."""
        return {
            "failure_threshold": self.circuit_breaker_failure_threshold,
            "success_threshold": self.circuit_breaker_success_threshold,
            "timeout": self.circuit_breaker_timeout,
            "enabled": self.circuit_breaker_enabled,
        }
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# ============================================================================
# Global Settings Instance
# ============================================================================

# Singleton settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    This function creates a singleton settings instance on first call
    and returns the cached instance on subsequent calls.
    
    Returns:
        Settings: The global settings instance
        
    Raises:
        ValidationError: If configuration is invalid or missing required fields
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    
    This function forces a reload of the settings, useful for testing
    or when environment variables have changed.
    
    Returns:
        Settings: The newly loaded settings instance
    """
    global _settings
    _settings = Settings()
    return _settings

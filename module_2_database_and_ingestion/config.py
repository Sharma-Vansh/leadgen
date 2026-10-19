"""
Module 2 Configuration & Settings
Centralized configuration management with environment variable validation.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    class BaseSettings(BaseModel):
        def __init__(self, **values):
            # Read from os.environ
            env_values = {}
            for field_name in self.model_fields:
                if field_name in os.environ:
                    env_values[field_name] = os.environ[field_name]
            env_values.update(values)
            super().__init__(**env_values)

    class SettingsConfigDict:
        def __init__(self, **kwargs):
            pass

# Base directory paths
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Module2Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database Configuration (PostgreSQL 16 + pgvector)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen_db",
        description="Async database connection string for asyncpg"
    )
    SYNC_DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/leadgen_db",
        description="Synchronous database connection string for Alembic migrations"
    )
    DB_POOL_SIZE: int = Field(default=10, description="Async engine connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Max overflow connections")
    DB_POOL_TIMEOUT: float = Field(default=30.0, description="Connection pool timeout in seconds")
    DB_ECHO: bool = Field(default=False, description="Enable SQL query echoing")

    # Redis & Celery Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Primary Redis URL")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", description="Celery message broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", description="Celery result backend URL")
    INGESTION_QUEUE_NAME: str = Field(default="leadgen_ingest_queue", description="Default ingestion queue name")

    # Deduplication & Embeddings
    SIMILARITY_THRESHOLD: float = Field(
        default=0.92,
        ge=0.0,
        le=1.0,
        description="pgvector cosine similarity threshold for semantic deduplication"
    )
    EMBEDDING_MODEL_NAME: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformers embedding model"
    )
    EMBEDDING_DIMENSION: int = Field(default=384, description="Embedding vector dimension")

    # Liveness & HTTP Settings
    HTTP_TIMEOUT_SECONDS: float = Field(default=15.0, description="Timeout for external HTTP checks")
    LIVENESS_CONCURRENCY: int = Field(default=10, description="Max concurrent liveness check workers")
    LIVENESS_MAX_RETRIES: int = Field(default=2, description="Max retries for transient HTTP errors")

    # Notification & Alerts
    RESEND_API_KEY: Optional[str] = Field(default=None, description="Resend API key for deadline alerts")
    NOTIFICATION_EMAIL_FROM: str = Field(default="alerts@leadgen.dev", description="Sender email address")
    DEADLINE_ALERT_HOURS_MIN: int = Field(default=48, description="Minimum hours before deadline to alert")
    DEADLINE_ALERT_HOURS_MAX: int = Field(default=72, description="Maximum hours before deadline to alert")

    # Fallback & Offline Testing
    TEST_DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///:memory:",
        description="In-memory SQLite connection for isolated offline testing"
    )


# Singleton settings instance
settings = Module2Settings()

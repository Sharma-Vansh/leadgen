"""
Module 3 Configuration & Settings
Environment variables, JWT secrets, and AI Matching Engine hyperparameters.
"""
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    # App Information
    APP_NAME: str = "LeadGen REST API & AI Matching Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",      # Student Next.js Web Dashboard
        "http://localhost:8080",
        "http://localhost:8085",      # Admin UI
        "chrome-extension://*",       # Autofill Chrome Extension
        "*"
    ]

    # JWT Authentication
    JWT_SECRET_KEY: str = "leadgen-dev-insecure-secret-key-change-in-production-937293749"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24        # 24 Hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7                # 7 Days

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen_db"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/leadgen_db"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"

    # AI Matching Engine
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    DEFAULT_MIN_MATCH_SCORE: float = 40.0             # Percent
    HIGH_MATCH_THRESHOLD: float = 80.0
    GOOD_MATCH_THRESHOLD: float = 60.0

    # Weight distribution for hybrid scoring
    WEIGHT_SKILL_OVERLAP: float = 0.40
    WEIGHT_SEMANTIC_SIMILARITY: float = 0.40
    WEIGHT_PREFERENCES: float = 0.20

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

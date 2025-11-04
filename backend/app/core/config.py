"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # API metadata
    app_name: str = "RI CTC Calculator API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"

    # CORS settings - can be overridden via environment variable
    cors_origins: List[str] = [
        "http://localhost:3000",  # Next.js dev
        "http://localhost:8000",  # FastAPI dev
    ]

    # Production frontend URL (set via environment variable)
    frontend_url: str | None = None

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

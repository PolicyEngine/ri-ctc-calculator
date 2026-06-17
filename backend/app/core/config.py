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
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:8080",
        "https://policyengine.org",
        "https://www.policyengine.org",
        "https://ri-ctc-calculator.policyengine.org",
        "https://ri-ctc-calculator.vercel.app",
    ]
    cors_origin_regex: str | None = (
        r"https://ri-ctc-calculator-[a-z0-9-]+-policy-engine\.vercel\.app"
    )

    # Production frontend URL (set via environment variable)
    frontend_url: str | None = None

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

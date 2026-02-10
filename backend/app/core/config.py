# Core settings and configuration
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str = "Deli API"
    app_version: str = "0.1.0"
    debug: bool = False
    db_echo: bool = False # Enable SQL echo (independent of debug mode)
    dev_mode: bool = False  # Enable mock auth and seed data in development
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/deli"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Notion OAuth
    notion_client_id: str = ""
    notion_client_secret: str = ""
    notion_redirect_uri: str = "http://localhost:8000/api/v1/auth/notion/callback"
    
    # OpenAI / Gemini
    openai_api_key: str = ""
    gemini_api_key: str = "" # Native Gemini API Key
    openai_model: str = "gemini-3-flash" # Default model name
    openai_base_url: str | None = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    refresh_token_expire_minutes: int = 60 * 24 * 30  # 30 days
    
    # FSRS
    fsrs_weights: list[float] = [
        0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01,
        1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

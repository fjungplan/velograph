from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cycling:cycling@postgres:5432/cycling_lineage"
    
    # Application
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Cycling Team Lineage"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Timeline cache
    TIMELINE_CACHE_ENABLED: bool = True
    TIMELINE_CACHE_TTL_SECONDS: int = 300
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()

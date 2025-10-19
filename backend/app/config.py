"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Meal Planner API"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql://mealplanner:password@localhost:5432/mealplanner_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # External APIs
    OPENFOODFACTS_API_URL: str = "https://world.openfoodfacts.org/api/v2"
    USDA_API_KEY: str = "DEMO_KEY"
    USDA_API_URL: str = "https://api.nal.usda.gov/fdc/v1"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

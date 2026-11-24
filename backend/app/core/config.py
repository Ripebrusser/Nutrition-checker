"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Indian Nutrition & Diet Planner"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Data paths
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    RECIPES_PARQUET_PATH: str = os.getenv("RECIPES_PARQUET_PATH", "./data/processed/recipes.parquet")

    class Config:
        # Read the backend's own .env (not the project-root Streamlit one) and
        # ignore unrelated keys such as STREAMLIT_PORT.
        env_file = str(BACKEND_ENV_FILE)
        case_sensitive = True
        extra = "ignore"


settings = Settings()
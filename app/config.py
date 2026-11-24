"""Configuration management for the application."""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings:
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Indian Nutrition & Diet Planner"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///data/app.db"
    
    # JWT
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Data paths
    RECIPES_PATH: str = "data/processed/recipes.parquet"
    PARSED_INGREDIENTS_PATH: str = "data/interim/phase2/parsed_recipe_ingredients.parquet"
    IFCT_PATH: str = "data/interim/ifct_final_candidate/ifct_table1_candidate.parquet"
    IFCT_MATCH_CANDIDATES_PATH: str = "data/interim/phase3/stage2_3/ifct_match_candidates.parquet"
    APPROVED_MAPPINGS_PATH: str = "data/processed/phase3/approved_mappings.jsonl"
    
    # Streamlit
    STREAMLIT_PORT: int = 8501
    STREAMLIT_ADDRESS: str = "0.0.0.0"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    def __init__(self):
        # Load from .env if exists
        from pathlib import Path
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if hasattr(self, key):
                            # Type conversion
                            current = getattr(self, key)
                            if isinstance(current, bool):
                                setattr(self, key, value.lower() in ("true", "1", "yes"))
                            elif isinstance(current, int):
                                setattr(self, key, int(value))
                            else:
                                setattr(self, key, value)


settings = Settings()
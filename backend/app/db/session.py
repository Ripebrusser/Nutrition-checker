"""Database session management for FastAPI backend."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.db.models import Base
from pathlib import Path
import os

# Database URL - SQLite for local development.
# The default is anchored to backend/data/app.db so the database is the same
# file no matter which directory the server is started from.
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "data" / "app.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# SQLite will not create missing parent directories, so make sure the folder exists.
if DATABASE_URL.startswith("sqlite:///"):
    _db_file = Path(DATABASE_URL[len("sqlite:///"):])
    if str(_db_file) != ":memory:":
        _db_file.parent.mkdir(parents=True, exist_ok=True)

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    # Import all models to ensure they're registered
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def init_recipe_data() -> None:
    """Initialize recipe data from parquet files if database is empty."""
    from app.db.models import Recipe
    db = SessionLocal()
    try:
        # Check if recipes already exist
        count = db.query(Recipe).count()
        if count > 0:
            return

        # Load recipes from parquet file
        import pandas as pd
        from pathlib import Path

        data_path = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "recipes.parquet"
        if not data_path.exists():
            # Try alternative path
            data_path = Path(__file__).parent.parent.parent.parent / "datasets" / "recipes.parquet"
        
        if not data_path.exists():
            print(f"Recipe dataset not found at {data_path}; recipes will be empty")
            return

        def text(row, *keys) -> str:
            """First non-empty string value among keys (the parquet uses *_en names)."""
            for key in keys:
                value = row.get(key)
                if isinstance(value, str) and value.strip():
                    return value
            return ""

        def number(row, key, default=0) -> int:
            value = row.get(key)
            try:
                if value is None or pd.isna(value):
                    return default
                return int(value)
            except (TypeError, ValueError):
                return default

        df = pd.read_parquet(data_path)
        for _, row in df.iterrows():
            recipe = Recipe(
                recipe_id=number(row, 'recipe_id'),
                recipe_name=text(row, 'recipe_name_en', 'recipe_name', 'recipe_name_original'),
                cuisine=text(row, 'cuisine'),
                course=text(row, 'course'),
                diet_labels=text(row, 'diet_labels'),
                recipe_type=text(row, 'recipe_type'),
                prep_time_min=number(row, 'prep_time_min'),
                cook_time_min=number(row, 'cook_time_min'),
                total_time_min=number(row, 'total_time_min'),
                servings=number(row, 'servings', 1),
                ingredients=text(row, 'ingredients_en', 'ingredients', 'ingredients_raw'),
                instructions=text(row, 'instructions_en', 'instructions', 'instructions_raw'),
                image_url=text(row, 'image_url') or None,
            )
            db.add(recipe)
        db.commit()
        print(f"Loaded {len(df)} recipes into database")
    except Exception as e:
        print(f"Error loading recipe data: {e}")
        db.rollback()
    finally:
        db.close()
"""Database session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from app.config import settings
from app.database.models import Base

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI/Streamlit to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a database session for manual management."""
    return SessionLocal()


def init_recipe_data() -> None:
    """Import recipe data from parquet files into database."""
    import pandas as pd
    from app.database.models import Recipe
    from app.database.session import SessionLocal
    
    db = SessionLocal()
    try:
        # Check if recipes already exist
        existing = db.query(Recipe).count()
        if existing > 0:
            print(f"Recipes already imported ({existing} records)")
            return
        
        print("Importing recipes from parquet...")
        df = pd.read_parquet("data/processed/recipes.parquet")
        
        for _, row in df.iterrows():
            # Parse diet_labels
            diet_labels = []
            if row.get('diet_labels') and isinstance(row['diet_labels'], str):
                diet_labels = [d.strip() for d in row['diet_labels'].split('|') if d.strip()]
            
            recipe = Recipe(
                recipe_id=int(row['recipe_id']),
                recipe_name=row['recipe_name_en'],
                cuisine=row['cuisine'],
                course=row['course'],
                diet_labels=diet_labels,
                recipe_type=row['recipe_type'],
                prep_time_min=int(row['prep_time_min']) if pd.notna(row['prep_time_min']) else 0,
                cook_time_min=int(row['cook_time_min']) if pd.notna(row['cook_time_min']) else 0,
                total_time_min=int(row['total_time_min']) if pd.notna(row['total_time_min']) else 0,
                servings=int(row['servings']) if pd.notna(row['servings']) else 4,
                ingredients_raw=row['ingredients_raw'],
                ingredients_en=row['ingredients_en'],
                instructions_raw=row['instructions_raw'],
                instructions_en=row['instructions_en'],
                source_url=row['source_url'],
                source_domain=row['source_domain'],
                nutrition_status='UNAVAILABLE',  # No approved mappings yet
            )
            db.add(recipe)
        
        db.commit()
        print(f"Imported {len(df)} recipes")
        
    except Exception as e:
        db.rollback()
        print(f"Error importing recipes: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    init_recipe_data()
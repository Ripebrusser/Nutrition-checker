"""Persistence layer for review decisions."""

import pandas as pd
from pathlib import Path
from datetime import datetime
import uuid
import pandas as pd

DECISIONS_DIR = Path("data/interim/phase3/decisions")
DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
DECISIONS_FILE = DECISIONS_DIR / "review_decisions.parquet"
DECISIONS_HISTORY_FILE = DECISIONS_DIR / "review_decisions_history.parquet"


def load_decisions() -> pd.DataFrame:
    """Load existing decisions from persistence."""
    if DECISIONS_FILE.exists():
        try:
            df = pd.read_parquet(DECISIONS_FILE)
            return df
        except Exception as e:
            print(f"Could not load decisions: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


def save_decisions(df: pd.DataFrame):
    """Save decisions to persistence."""
    try:
        df.to_parquet(DECISIONS_FILE, index=False)
        # Also save history
        if DECISIONS_HISTORY_FILE.exists():
            hist = pd.read_parquet(DECISIONS_HISTORY_FILE)
            hist = pd.concat([hist, df], ignore_index=True)
        else:
            hist = df.copy()
        hist.to_parquet(DECISIONS_HISTORY_FILE, index=False)
    except Exception as e:
        print(f"Failed to save decisions: {e}")


def get_existing_decision(decisions_df, review_unit_id: str):
    """Get existing decision for a review unit."""
    if decisions_df is not None and not decisions_df.empty:
        matches = decisions_df[decisions_df['review_unit_id'] == review_unit_id]
        if not matches.empty:
            return matches.iloc[-1]  # Return most recent
    return None
"""Load Phase 1 canonical restaurant tables from disk."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_canonical_parquet(path: str | Path) -> pd.DataFrame:
    """Read ``canonical_restaurants.parquet`` (or equivalent) into a DataFrame."""
    return pd.read_parquet(Path(path))

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import pandas as pd

from phase1.ingestion.constants import DATASET_ID

SourceKind = Literal["huggingface", "csv"]


def _ensure_hf_cache_dirs(cache_dir: Path) -> None:
    cache_dir = cache_dir.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache_dir))
    os.environ.setdefault("HF_DATASETS_CACHE", str(cache_dir / "datasets"))


def load_from_huggingface(cache_dir: Path) -> pd.DataFrame:
    """Download / load the Zomato CSV via Hugging Face `datasets` into a pandas DataFrame."""
    from datasets import load_dataset

    _ensure_hf_cache_dirs(cache_dir)
    ds = load_dataset(DATASET_ID, cache_dir=str(cache_dir), trust_remote_code=True)
    split = "train" if "train" in ds else list(ds.keys())[0]
    return ds[split].to_pandas()


def load_from_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[])


def load_raw(
    *,
    source: SourceKind,
    cache_dir: Path,
    csv_path: Path | None,
) -> pd.DataFrame:
    if source == "csv":
        if not csv_path or not csv_path.is_file():
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        return load_from_csv(csv_path)
    return load_from_huggingface(cache_dir)

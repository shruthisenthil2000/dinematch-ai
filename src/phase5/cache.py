"""Optional response cache: hash(prefs + dataset fingerprint + pipeline options)."""

from __future__ import annotations

import hashlib
import json
import threading
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


def dataset_fingerprint(parquet_path: Path) -> str:
    """Stable-ish version token: manifest when present, else file mtime + size."""
    manifest = parquet_path.parent / "dataset_manifest.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            gen = str(data.get("generated_at", ""))
            rev = str(data.get("dataset_revision", ""))
            rows = data.get("row_counts") or {}
            n = rows.get("canonical_after_dedupe")
            return f"manifest|{gen}|{rev}|{n}"
        except (OSError, json.JSONDecodeError):
            pass
    try:
        st = parquet_path.stat()
        return f"file|mtime_ns={st.st_mtime_ns}|size={st.st_size}"
    except OSError:
        return "file|missing"


def cache_key(
    preferences: Mapping[str, Any],
    *,
    dataset_fp: str,
    cap: int,
    top_n: int,
    use_llm: bool,
) -> str:
    payload = json.dumps(dict(preferences), sort_keys=True, default=str)
    basis = f"{payload}|ds={dataset_fp}|cap={cap}|top_n={top_n}|llm={use_llm}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


class ResponseCache:
    """In-memory LRU cache with optional JSON persistence under ``cache_dir``."""

    def __init__(self, *, max_entries: int = 256, cache_dir: Path | None = None) -> None:
        self._max_entries = max(1, int(max_entries))
        self._cache_dir = cache_dir
        self._mem: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = threading.Lock()
        if self._cache_dir is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            if key in self._mem:
                self._mem.move_to_end(key)
                return deepcopy(self._mem[key])
        if self._cache_dir is not None:
            path = self._cache_dir / f"{key}.json"
            if path.is_file():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        with self._lock:
                            self._mem[key] = deepcopy(data)
                            self._mem.move_to_end(key)
                            self._evict_if_needed_unlocked()
                        return deepcopy(data)
                except (OSError, json.JSONDecodeError):
                    return None
        return None

    def set(self, key: str, value: dict[str, Any]) -> None:
        copy = deepcopy(value)
        with self._lock:
            self._mem[key] = copy
            self._mem.move_to_end(key)
            self._evict_if_needed_unlocked()
        if self._cache_dir is not None:
            path = self._cache_dir / f"{key}.json"
            try:
                path.write_text(json.dumps(copy, indent=2, default=str), encoding="utf-8")
            except OSError:
                pass

    def _evict_if_needed_unlocked(self) -> None:
        while len(self._mem) > self._max_entries:
            self._mem.popitem(last=False)

    def clear_memory(self) -> None:
        with self._lock:
            self._mem.clear()


_GLOBAL: ResponseCache | None = None
_GLOBAL_LOCK = threading.Lock()


def get_global_cache(*, max_entries: int = 256, cache_dir: Path | None = None) -> ResponseCache:
    """Process-wide cache singleton (Flask dev server / CLI reuse)."""
    global _GLOBAL
    with _GLOBAL_LOCK:
        if _GLOBAL is None:
            _GLOBAL = ResponseCache(max_entries=max_entries, cache_dir=cache_dir)
        return _GLOBAL


def reset_global_cache_for_tests() -> None:
    global _GLOBAL
    with _GLOBAL_LOCK:
        _GLOBAL = None

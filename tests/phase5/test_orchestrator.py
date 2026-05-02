"""Phase 5 orchestrator and cache."""

from __future__ import annotations

import pandas as pd

from phase5.cache import ResponseCache, cache_key, dataset_fingerprint, reset_global_cache_for_tests
from phase5.orchestrator import run_recommendation


def _minimal_parquet(path, *, city: str = "Pune", band: str = "medium") -> None:
    df = pd.DataFrame(
        [
            {
                "restaurant_id": "aa",
                "name": "Alpha",
                "city": city,
                "cuisines": ["italian"],
                "rating": 4.5,
                "votes": 10,
                "cost_band": band,
            }
        ]
    )
    df.to_parquet(path, index=False)


def test_run_recommendation_offline(tmp_path):
    pq = tmp_path / "c.parquet"
    _minimal_parquet(pq)
    prefs = {"location": "Pune", "budget": "medium", "cuisines": [], "min_rating": 0.0}
    response, metrics = run_recommendation(
        prefs,
        parquet_path=pq,
        use_llm=False,
        use_cache=False,
    )
    assert len(response["recommendations"]) == 1
    assert response["recommendations"][0]["name"] == "Alpha"
    assert metrics.candidate_count == 1
    assert metrics.cache_hit is False
    assert metrics.prompt_chars > 0


def test_cache_hit_second_call(tmp_path):
    reset_global_cache_for_tests()
    pq = tmp_path / "c.parquet"
    _minimal_parquet(pq)
    prefs = {"location": "Pune", "budget": "medium", "cuisines": [], "min_rating": 0.0}
    cache = ResponseCache(max_entries=8)
    _, m1 = run_recommendation(
        prefs,
        parquet_path=pq,
        use_llm=False,
        use_cache=True,
        cache=cache,
    )
    _, m2 = run_recommendation(
        prefs,
        parquet_path=pq,
        use_llm=False,
        use_cache=True,
        cache=cache,
    )
    assert m1.cache_hit is False
    assert m2.cache_hit is True


def test_cache_key_stable():
    prefs = {"location": "Pune", "budget": "medium", "cuisines": [], "min_rating": 0.0}
    k1 = cache_key(prefs, dataset_fp="fp1", cap=25, top_n=5, use_llm=False)
    k2 = cache_key(prefs, dataset_fp="fp1", cap=25, top_n=5, use_llm=False)
    assert k1 == k2


def test_dataset_fingerprint_file(tmp_path):
    pq = tmp_path / "x.parquet"
    pq.write_bytes(b"")
    fp = dataset_fingerprint(pq)
    assert fp.startswith("file|")

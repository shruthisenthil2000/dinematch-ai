"""Deterministic pre-LLM scoring and ordering for Phase 3 candidates."""

from __future__ import annotations

from typing import Any

import pandas as pd

from phase3.retrieval.filtering import _normalize_cuisine_tokens


def retrieval_score_series(df: pd.DataFrame, user_tokens: set[str]) -> pd.Series:
    """
    Pre-LLM score: rating × cuisine_match weight.

    Cuisine weight is 1.0 when the user lists no cuisines; otherwise overlap count
    divided by the number of user cuisine tokens (preference match boost).
    """

    def rating_val(r: Any) -> float:
        if r is None or (isinstance(r, float) and pd.isna(r)):
            return 0.0
        return float(r)

    ratings = df["rating"].map(rating_val)

    if not user_tokens:
        cuisine_weight = pd.Series(1.0, index=df.index)
    else:
        n_user = max(len(user_tokens), 1)

        def weight(cell: Any) -> float:
            rest = _normalize_cuisine_tokens(cell)
            overlap = len(user_tokens & rest)
            return float(overlap) / float(n_user)

        cuisine_weight = df["cuisines"].map(weight)

    return ratings * cuisine_weight


def sort_candidates_mergesort(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stable sort: retrieval_score desc, votes desc, rating desc, restaurant_id asc.
    Expects column ``retrieval_score``; drops temporary ordering columns.
    """
    votes_ord = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype("int64")
    rating_ord = pd.to_numeric(df["rating"], errors="coerce").fillna(-1.0)
    work = df.assign(_votes_ord=votes_ord, _rating_ord=rating_ord)
    work = work.sort_values(
        by=["retrieval_score", "_votes_ord", "_rating_ord", "restaurant_id"],
        ascending=[False, False, False, True],
        kind="mergesort",
    )
    return work.drop(columns=["_votes_ord", "_rating_ord"])


def apply_candidate_cap(df: pd.DataFrame, cap: int) -> pd.DataFrame:
    return df.head(cap).reset_index(drop=True)


def diversify_by_locality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Light deterministic diversification pass over a pre-sorted frame.

    Keeps the original relative ranking inside each locality bucket, then interleaves
    buckets round-robin so a single dense area does not dominate the first page.
    """
    if "locality" not in df.columns or len(df) <= 1:
        return df
    localities = (
        df["locality"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", "__unknown__")
    )
    work = df.copy()
    work["_loc_bucket"] = localities

    groups: dict[str, list[int]] = {}
    order: list[str] = []
    for idx, bucket in zip(work.index.tolist(), work["_loc_bucket"].tolist()):
        if bucket not in groups:
            groups[bucket] = []
            order.append(bucket)
        groups[bucket].append(idx)

    picks: list[int] = []
    progressed = True
    while progressed:
        progressed = False
        for bucket in order:
            rows = groups[bucket]
            if rows:
                picks.append(rows.pop(0))
                progressed = True

    return work.loc[picks].drop(columns=["_loc_bucket"])

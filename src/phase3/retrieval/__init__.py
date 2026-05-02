"""Structured retrieval: load canonical data, filter, rank, cap."""

from phase3.retrieval.filter_engine import retrieve_candidates
from phase3.retrieval.filtering import (
    REQUIRED_COLUMNS,
    cuisine_cell_to_sequence,
    preference_filter_mask,
    user_cuisine_tokens,
    validate_canonical_frame,
)
from phase3.retrieval.load_table import load_canonical_parquet
from phase3.retrieval.ranking import (
    apply_candidate_cap,
    retrieval_score_series,
    sort_candidates_mergesort,
)

__all__ = [
    "REQUIRED_COLUMNS",
    "apply_candidate_cap",
    "cuisine_cell_to_sequence",
    "load_canonical_parquet",
    "preference_filter_mask",
    "retrieve_candidates",
    "retrieval_score_series",
    "sort_candidates_mergesort",
    "user_cuisine_tokens",
    "validate_canonical_frame",
]

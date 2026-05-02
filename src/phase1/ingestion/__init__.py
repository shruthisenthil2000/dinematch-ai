"""Phase 1 ingestion package: load, normalize, convert, pipeline."""

from phase1.ingestion.pipeline import PipelineResult, run_pipeline

__all__ = ["PipelineResult", "run_pipeline"]

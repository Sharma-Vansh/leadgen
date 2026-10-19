"""
Ingestion Pipeline Package
Exports Stage 1 validator, Stage 2 normalizer, Stage 3 deduplicator, Stage 4 writer,
Stage 5 liveness service, and Master PipelineManager.
"""
from module_2_database_and_ingestion.ingestion.stage1_validator import Stage1Validator, ValidationResult
from module_2_database_and_ingestion.ingestion.stage2_normalizer import (
    SalaryConverter,
    LocationCleaner,
    DateParser,
    TypeClassifier
)
from module_2_database_and_ingestion.ingestion.stage3_deduplicator import HashDeduplicator, VectorDeduplicator
from module_2_database_and_ingestion.ingestion.stage4_writer import Stage4Writer, IngestionSummary
from module_2_database_and_ingestion.ingestion.stage5_liveness import Stage5LivenessService, LivenessCheckResult
from module_2_database_and_ingestion.ingestion.pipeline_manager import PipelineManager, PipelineExecutionReport

__all__ = [
    "Stage1Validator",
    "ValidationResult",
    "SalaryConverter",
    "LocationCleaner",
    "DateParser",
    "TypeClassifier",
    "HashDeduplicator",
    "VectorDeduplicator",
    "Stage4Writer",
    "IngestionSummary",
    "Stage5LivenessService",
    "LivenessCheckResult",
    "PipelineManager",
    "PipelineExecutionReport"
]

"""
Pipeline Manager: Master Ingestion Orchestrator
Coordinates the 5-stage ingestion pipeline from raw payloads to transactional persistence.
Includes correlation ID tracking, stage timing metrics, and structured reports.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
import uuid
import logging
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from module_2_database_and_ingestion.ingestion.stage1_validator import Stage1Validator, ValidationResult
from module_2_database_and_ingestion.ingestion.stage2_normalizer import (
    SalaryConverter,
    LocationCleaner,
    DateParser,
    TypeClassifier
)
from module_2_database_and_ingestion.ingestion.stage4_writer import Stage4Writer, IngestionSummary

logger = logging.getLogger("PipelineManager")


@dataclass
class PipelineExecutionReport:
    correlation_id: str
    started_at: str
    completed_at: str
    duration_ms: float
    total_received: int
    validation_passed: int
    validation_rejected: int
    inserted: int
    merged: int
    updated: int
    failed: int
    rejections: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class PipelineManager:
    """Master orchestrator executing the 5-stage LeadGen ingestion workflow."""

    @classmethod
    def normalize_record(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """Runs Stage 2 normalization across salary, location, dates, and job types."""
        norm = dict(record)

        # 1. Salary Normalization
        raw_sal = norm.get("salary_raw")
        s_min, s_max, s_curr = SalaryConverter.convert(raw_sal)
        if s_min is not None or s_max is not None:
            norm["salary_min"] = s_min
            norm["salary_max"] = s_max
            norm["salary_currency"] = s_curr

        # 2. Location Normalization
        raw_loc = norm.get("location")
        clean_loc, is_rem, country, city = LocationCleaner.clean(raw_loc)
        norm["location"] = clean_loc
        norm["is_remote"] = is_rem
        norm["country"] = country
        norm["city"] = city

        # 3. Date Normalization
        raw_posted = norm.get("posted_date")
        if raw_posted:
            norm["posted_date"] = DateParser.parse(raw_posted) if isinstance(raw_posted, str) else raw_posted

        raw_deadline = norm.get("deadline")
        if raw_deadline:
            norm["deadline"] = DateParser.parse(raw_deadline) if isinstance(raw_deadline, str) else raw_deadline

        raw_scraped = norm.get("scraped_at")
        if raw_scraped:
            norm["scraped_at"] = DateParser.parse(raw_scraped) if isinstance(raw_scraped, str) else raw_scraped
        else:
            norm["scraped_at"] = datetime.now(timezone.utc)

        # 4. Employment Type Classification
        raw_type = norm.get("employment_type")
        title = norm.get("title")
        clean_type, _ = TypeClassifier.classify(raw_type, title)
        norm["employment_type"] = clean_type

        return norm

    @classmethod
    async def process_batch(
        cls,
        session: AsyncSession,
        records: List[Any],
        correlation_id: Optional[str] = None
    ) -> PipelineExecutionReport:
        """
        Executes the ingestion pipeline on a batch of raw records.
        """
        cid = correlation_id or f"ingest-{uuid.uuid4().hex[:8]}"
        t_start = time.perf_counter()
        start_time_iso = datetime.now(timezone.utc).isoformat()

        logger.info(f"[{cid}] Starting ingestion batch of {len(records)} records...")

        # --- Stage 1: Validation Gate ---
        val_result: ValidationResult = Stage1Validator.validate_batch(records)

        # --- Stage 2: Normalization Engine ---
        normalized_records: List[Dict[str, Any]] = []
        for valid_rec in val_result.valid_records:
            try:
                norm_rec = cls.normalize_record(valid_rec)
                normalized_records.append(norm_rec)
            except Exception as e:
                logger.error(f"[{cid}] Normalization failed for '{valid_rec.get('title')}': {e}")
                val_result.rejected_records.append({
                    "raw_payload": valid_rec,
                    "reason": f"Normalization exception: {str(e)}"
                })

        # --- Stages 3 & 4: Deduplication & Atomic Persistence ---
        writer_summary: IngestionSummary = await Stage4Writer.write_batch(
            session=session,
            normalized_records=normalized_records
        )

        t_end = time.perf_counter()
        duration_ms = round((t_end - t_start) * 1000, 2)
        end_time_iso = datetime.now(timezone.utc).isoformat()

        report = PipelineExecutionReport(
            correlation_id=cid,
            started_at=start_time_iso,
            completed_at=end_time_iso,
            duration_ms=duration_ms,
            total_received=len(records),
            validation_passed=val_result.valid_count,
            validation_rejected=val_result.rejected_count,
            inserted=writer_summary.inserted,
            merged=writer_summary.merged,
            updated=writer_summary.updated,
            failed=writer_summary.failed,
            rejections=val_result.rejected_records,
            errors=writer_summary.errors
        )

        logger.info(
            f"[{cid}] Pipeline completed in {duration_ms}ms: "
            f"{report.inserted} inserted, {report.merged} merged, "
            f"{report.updated} updated, {report.validation_rejected} rejected, {report.failed} failed."
        )
        return report

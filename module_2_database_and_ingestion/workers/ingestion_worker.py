"""
Ingestion Worker
Consumes batches of job listings from Redis / message broker and executes the 5-stage pipeline.
Also supports processing from the local Module 1 JSONL buffer (leadgen_ingest_queue.jsonl).
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from module_2_database_and_ingestion.workers.celery_app import app
from module_2_database_and_ingestion.db.session import get_async_session
from module_2_database_and_ingestion.ingestion.pipeline_manager import PipelineManager, PipelineExecutionReport

logger = logging.getLogger("IngestionWorker")


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_ingestion_batch(self, records: List[Dict[str, Any]], correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Celery task that ingests a batch of job listings into the database.
    """
    logger.info(f"[IngestionWorker] Received batch of {len(records)} records for processing.")

    async def _run():
        async with get_async_session() as session:
            report: PipelineExecutionReport = await PipelineManager.process_batch(
                session=session,
                records=records,
                correlation_id=correlation_id
            )
            return {
                "correlation_id": report.correlation_id,
                "duration_ms": report.duration_ms,
                "inserted": report.inserted,
                "merged": report.merged,
                "updated": report.updated,
                "rejected": report.validation_rejected,
                "failed": report.failed
            }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error(f"[IngestionWorker] Task failed: {exc}")
        raise self.retry(exc=exc)


def consume_jsonl_buffer(file_path: str, batch_size: int = 50) -> int:
    """
    Synchronously drains the local Module 1 JSONL queue buffer into the pipeline.
    Useful for local offline development without a live Redis server.
    """
    p = Path(file_path)
    if not p.exists():
        logger.warning(f"[IngestionWorker] Buffer file {file_path} does not exist.")
        return 0

    lines = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                try:
                    lines.append(json.loads(line_str))
                except json.JSONDecodeError:
                    continue

    if not lines:
        return 0

    total_processed = 0
    for i in range(0, len(lines), batch_size):
        chunk = lines[i:i + batch_size]
        result = process_ingestion_batch(chunk, correlation_id=f"buffer-{i}")
        total_processed += result.get("inserted", 0) + result.get("merged", 0)

    # Clear processed buffer
    p.unlink(missing_ok=True)
    logger.info(f"[IngestionWorker] Emptied buffer and processed {total_processed} listings.")
    return total_processed

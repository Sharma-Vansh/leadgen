"""
Archetype E Emitter: Central Queue Publisher
Receives verified job listings from high-defense scrapers and publishes them
into the central database queue (Redis / RabbitMQ / Module 2 drop-zone).
"""
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.config import OUTPUT_DIR

logger = logging.getLogger("QueuePublisher")


class QueuePublisher:
    def __init__(self, queue_name: str = "leadgen_ingest_queue"):
        self.queue_name = queue_name
        self.queue_file = OUTPUT_DIR / f"{queue_name}.jsonl"

    async def publish(self, listing: StandardJobListing) -> bool:
        """Appends verified listing to JSONL queue buffer."""
        try:
            with open(self.queue_file, "a", encoding="utf-8") as f:
                f.write(listing.model_dump_json() + "\n")
            logger.debug(f"[QueuePublisher] Published job {listing.id} to {self.queue_name}")
            return True
        except Exception as e:
            logger.error(f"[QueuePublisher] Failed to publish job: {e}")
            return False

    async def publish_batch(self, listings: List[StandardJobListing]) -> int:
        """Publishes a batch of listings."""
        count = 0
        for item in listings:
            if await self.publish(item):
                count += 1
        logger.info(f"[QueuePublisher] Successfully queued {count} records into {self.queue_name}.")
        return count

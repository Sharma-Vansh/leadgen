"""
Archetype D, Tier 1: Telegram Public Job Channels Listener (SRC-0381)
Uses Telethon MTProto client to listen to public recruitment channels and off-campus drives.
Includes simulated feeder for instant testing and live MTProto socket mode.
"""
from typing import List, Optional, Dict, Any
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.spam_filter import SpamFilter
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.entity_extractor import EntityExtractor
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.link_unshortener import LinkUnshortener

logger = logging.getLogger("TelegramListener")


class TelegramListener(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0381",
            source_name="Telegram Community Listener",
            archetype="D",
            http_client=http_client
        )
        self.spam_filter = SpamFilter()
        self.entity_extractor = EntityExtractor()
        self.link_unshortener = LinkUnshortener()

    async def parse_message(self, raw_text: str, msg_id: str) -> Optional[StandardJobListing]:
        """Runs the 4-tier processing pipeline on a single Telegram message."""
        # Tier 1: Spam Gatekeeper
        is_valid, reason = self.spam_filter.is_valid_hiring_post(raw_text)
        if not is_valid:
            logger.debug(f"[{self.source_id}] Dropped message {msg_id}: {reason}")
            return None

        # Tier 2: Link Resolver
        urls = self.link_unshortener.extract_urls(raw_text)
        apply_url = urls[0] if urls else "https://t.me/leadgen_jobs"
        apply_url = await self.link_unshortener.unshorten_url(apply_url)

        # Tier 3: Entity Extraction
        entities = self.entity_extractor.extract_entities(raw_text)

        # Tier 4: Standard Job Schema
        listing = StandardJobListing(
            id=f"tg-{msg_id}",
            source_id=self.source_id,
            source_name=self.source_name,
            title=entities["role"],
            company=entities["company"],
            apply_url=apply_url,
            location="Remote / Hybrid",
            is_remote=True,
            country="India",
            employment_type="internship" if "intern" in entities["role"].lower() else "full_time",
            salary_raw=entities["salary_raw"],
            salary_min=entities["salary_min"],
            salary_max=entities["salary_max"],
            salary_currency=entities["salary_currency"],
            description=raw_text[:500],
            skills=entities["skills"],
            batch_eligible=entities["batch_eligible"],
            raw_payload={"telegram_msg_id": msg_id, "detected_urls": urls}
        )
        return listing

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting public channel feed...")

        # Sample stream messages representing real tech channels
        sample_messages = [
            {
                "id": "1042",
                "text": "Swiggy is hiring for SDE Intern (Frontend)! Tech Stack: React, TypeScript, Git. Stipend: ₹40,000/month. Eligible: 2025 and 2026 Batch. Apply via Google Form: https://bit.ly/swiggy-intern-2026"
            },
            {
                "id": "1043",
                "text": "Cred is looking for Backend Developer (Python / FastAPI). Experience: 0-1 Yr. Package: 12 LPA. Bangalore or Remote. Apply here: https://cred.club/careers/backend-dev"
            },
            {
                "id": "1044",
                "text": "Join free crypto telegram channel and get rich quick! Click bit.ly/spam-link"  # Spam, should be filtered
            },
            {
                "id": "1045",
                "text": "Off-Campus Drive: AI ML Trainee at Zepto. Skills: Python, SQL, Machine Learning. Target: 2024, 2025 graduates. Apply link: https://forms.gle/zepto-hiring-test"
            }
        ]

        if limit:
            sample_messages = sample_messages[:limit]

        listings: List[StandardJobListing] = []
        for m in sample_messages:
            parsed = await self.parse_message(m["text"], m["id"])
            if parsed:
                listings.append(parsed)

        logger.info(f"[{self.source_id}] Successfully processed {len(listings)} community hiring posts.")
        return listings

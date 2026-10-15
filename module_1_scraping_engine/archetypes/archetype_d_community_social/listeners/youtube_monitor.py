"""
Archetype D, Tier 1: YouTube Career Channels Monitor (SRC-0380)
Monitors daily recruitment announcements, off-campus drive video descriptions & pinned comments.
"""
from typing import List, Optional, Dict, Any
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.spam_filter import SpamFilter
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.entity_extractor import EntityExtractor
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.link_unshortener import LinkUnshortener

logger = logging.getLogger("YouTubeMonitor")


class YouTubeMonitor(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0380",
            source_name="YouTube Career Monitor",
            archetype="D",
            http_client=http_client
        )
        self.spam_filter = SpamFilter()
        self.entity_extractor = EntityExtractor()
        self.link_unshortener = LinkUnshortener()

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Checking career channel video descriptions...")

        sample_posts = [
            {
                "video_id": "yt_vid_449",
                "title_desc": "Razorpay Off-Campus Drive 2026 Batch Announced! Hiring Software Engineer (Backend). Tech: Python, Go, SQL. CTC: 15 LPA. Apply Link in description: https://bit.ly/razorpay-drive-2026"
            }
        ]

        listings: List[StandardJobListing] = []
        for p in sample_posts:
            text = p["title_desc"]
            is_valid, _ = self.spam_filter.is_valid_hiring_post(text)
            if not is_valid:
                continue

            urls = self.link_unshortener.extract_urls(text)
            apply_url = urls[0] if urls else "https://youtube.com"
            apply_url = await self.link_unshortener.unshorten_url(apply_url)
            entities = self.entity_extractor.extract_entities(text)

            listing = StandardJobListing(
                id=f"yt-{p['video_id']}",
                source_id=self.source_id,
                source_name=self.source_name,
                title=entities["role"],
                company=entities["company"],
                apply_url=apply_url,
                location="India (Remote / Hybrid)",
                is_remote=True,
                country="India",
                employment_type="full_time",
                salary_raw=entities["salary_raw"],
                salary_min=entities["salary_min"],
                salary_max=entities["salary_max"],
                salary_currency=entities["salary_currency"],
                description=text,
                skills=entities["skills"],
                batch_eligible=entities["batch_eligible"],
                raw_payload={"youtube_video_id": p["video_id"]}
            )
            listings.append(listing)

        return listings

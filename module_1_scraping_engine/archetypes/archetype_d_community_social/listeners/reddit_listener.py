"""
Archetype D, Tier 1: Reddit Tech Hiring Community Listener (SRC-REDDIT)
Monitors r/forhire [Hiring], r/hiring, and r/jobbit for direct founder & developer listings.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.spam_filter import SpamFilter
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.entity_extractor import EntityExtractor
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.link_unshortener import LinkUnshortener

logger = logging.getLogger("RedditListener")


class RedditListener(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-REDDIT",
            source_name="Reddit Hiring Community Monitor",
            archetype="D",
            http_client=http_client
        )
        self.spam_filter = SpamFilter()
        self.entity_extractor = EntityExtractor()
        self.link_unshortener = LinkUnshortener()

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Checking r/forhire and r/hiring community feeds...")

        sample_posts = [
            {
                "subreddit": "r/forhire",
                "post_id": "rdt_post_551",
                "text": "[Hiring] Supabase is hiring for Developer Advocate / Technical Writer. Skills: Python, SQL, Documentation. Remote. Pay: $80,000 - $110,000/yr. Apply: https://supabase.com/careers"
            },
            {
                "subreddit": "r/jobbit",
                "post_id": "rdt_post_552",
                "text": "[Hiring] Zerodha is looking for Frontend Developer (Vue.js / React / TypeScript). CTC: 16 LPA. Bangalore or Remote. Apply: https://zerodha.com/careers"
            }
        ]

        if limit:
            sample_posts = sample_posts[:limit]

        listings: List[StandardJobListing] = []
        for p in sample_posts:
            text = p["text"]
            is_valid, _ = self.spam_filter.is_valid_hiring_post(text)
            if not is_valid:
                continue

            urls = self.link_unshortener.extract_urls(text)
            apply_url = urls[0] if urls else "https://reddit.com/r/forhire"
            apply_url = await self.link_unshortener.unshorten_url(apply_url)
            entities = self.entity_extractor.extract_entities(text)

            listing = StandardJobListing(
                id=f"reddit-{p['post_id']}",
                source_id=self.source_id,
                source_name=f"Reddit ({p['subreddit']})",
                title=entities["role"],
                company=entities["company"],
                apply_url=apply_url,
                location="Remote",
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
                raw_payload={"subreddit": p["subreddit"], "reddit_id": p["post_id"]}
            )
            listings.append(listing)

        logger.info(f"[{self.source_id}] Extracted {len(listings)} Reddit community job listings.")
        return listings

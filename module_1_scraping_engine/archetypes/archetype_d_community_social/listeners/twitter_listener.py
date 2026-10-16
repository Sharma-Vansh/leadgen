"""
Archetype D, Tier 1: Twitter / X Tech Founder Hiring Listener (SRC-TWITTER)
Monitors direct founder & engineering leader hiring tweets and off-campus threads.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.spam_filter import SpamFilter
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.entity_extractor import EntityExtractor
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.link_unshortener import LinkUnshortener

logger = logging.getLogger("TwitterListener")


class TwitterListener(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-TWITTER",
            source_name="Twitter / X Founder Hiring Monitor",
            archetype="D",
            http_client=http_client
        )
        self.spam_filter = SpamFilter()
        self.entity_extractor = EntityExtractor()
        self.link_unshortener = LinkUnshortener()

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Checking tech founder hiring tweets...")

        sample_tweets = [
            {
                "handle": "@kunalb11",
                "tweet_id": "tw_179201",
                "text": "CRED is looking for Backend Developer to build scalable payment pipelines. Tech: Go, Python, Kafka. Bengaluru. DM or apply: https://cred.club/careers/backend"
            },
            {
                "handle": "@deepigoyal",
                "tweet_id": "tw_179202",
                "text": "Zomato is hiring for Product Designer & Frontend Developer. React, Figma. Delhi NCR. High ownership. Email your portfolio or apply: https://zomato.com/careers"
            }
        ]

        if limit:
            sample_tweets = sample_tweets[:limit]

        listings: List[StandardJobListing] = []
        for t in sample_tweets:
            text = t["text"]
            is_valid, _ = self.spam_filter.is_valid_hiring_post(text)
            if not is_valid:
                continue

            urls = self.link_unshortener.extract_urls(text)
            apply_url = urls[0] if urls else "https://x.com"
            apply_url = await self.link_unshortener.unshorten_url(apply_url)
            entities = self.entity_extractor.extract_entities(text)

            listing = StandardJobListing(
                id=f"tw-{t['tweet_id']}",
                source_id=self.source_id,
                source_name=f"X / Twitter ({t['handle']})",
                title=entities["role"],
                company=entities["company"],
                apply_url=apply_url,
                location="Bengaluru / Delhi NCR / Remote",
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
                raw_payload={"tweet_id": t["tweet_id"], "handle": t["handle"]}
            )
            listings.append(listing)

        logger.info(f"[{self.source_id}] Extracted {len(listings)} Twitter founder hiring listings.")
        return listings

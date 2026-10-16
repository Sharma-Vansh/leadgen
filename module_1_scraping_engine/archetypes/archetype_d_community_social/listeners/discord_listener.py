"""
Archetype D, Tier 1: Discord Community Job Channel Listener (SRC-DISCORD)
Monitors tech, developer, and open-source Discord community job boards (Reactiflux, Python, Web3).
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.spam_filter import SpamFilter
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.entity_extractor import EntityExtractor
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.link_unshortener import LinkUnshortener

logger = logging.getLogger("DiscordListener")


class DiscordListener(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-DISCORD",
            source_name="Discord Developer Community Listener",
            archetype="D",
            http_client=http_client
        )
        self.spam_filter = SpamFilter()
        self.entity_extractor = EntityExtractor()
        self.link_unshortener = LinkUnshortener()

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Checking developer Discord channels for hiring notices...")

        sample_posts = [
            {
                "channel": "reactiflux #jobs",
                "id": "dsc_msg_101",
                "text": "Postman is hiring for Frontend Engineer (React / TypeScript). Remote (India). Salary: 18 - 25 LPA. DM me or apply at: https://postman.com/careers/fe-dev"
            },
            {
                "channel": "python-discord #job-board",
                "id": "dsc_msg_102",
                "text": "Groww is looking for Backend Engineer (Python / Django / AWS). 1-3 YOE. Bangalore / Hybrid. CTC: 20 LPA. Submit resume: https://groww.in/careers/backend-eng"
            },
            {
                "channel": "web3-builders #gigs",
                "id": "dsc_msg_103",
                "text": "Polygon is hiring for Full-Stack Developer Trainee. React, Node.js, Solidity. Remote worldwide. Stipend: $2,500/month. Apply link: https://polygon.technology/careers"
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
            apply_url = urls[0] if urls else "https://discord.com"
            apply_url = await self.link_unshortener.unshorten_url(apply_url)
            entities = self.entity_extractor.extract_entities(text)

            listing = StandardJobListing(
                id=f"discord-{p['id']}",
                source_id=self.source_id,
                source_name=f"Discord ({p['channel']})",
                title=entities["role"],
                company=entities["company"],
                apply_url=apply_url,
                location="Remote / Hybrid",
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
                raw_payload={"discord_channel": p["channel"], "discord_msg_id": p["id"]}
            )
            listings.append(listing)

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} Discord job listings.")
        return listings

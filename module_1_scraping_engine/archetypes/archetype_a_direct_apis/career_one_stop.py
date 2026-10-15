"""
Archetype A: CareerOneStop US Employment API Adapter (SRC-0387)
Docs: https://www.careeronestop.org/Developers/WebServices/apis.aspx
"""
from typing import List, Optional
import os
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("CareerOneStopScraper")


class CareerOneStopScraper(BaseScraper):
    API_URL = "https://api.careeronestop.org/v1/jobsearch"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0387",
            source_name="CareerOneStop",
            archetype="A",
            http_client=http_client
        )
        self.user_id = os.getenv("CAREERONESTOP_USER_ID", "")
        self.api_token = os.getenv("CAREERONESTOP_TOKEN", "")

    async def scrape(self, limit: Optional[int] = 50, keyword: str = "Software") -> List[StandardJobListing]:
        if not self.user_id or not self.api_token:
            logger.warning(
                f"[{self.source_id}] CareerOneStop credentials not found in environment. "
                "Register free at https://www.careeronestop.org/Developers/WebServices/apis.aspx to enable live calls."
            )
            return []

        url = f"{self.API_URL}/{self.user_id}/{keyword}/US/25/0/0/0/{limit or 20}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
        }
        logger.info(f"[{self.source_id}] Fetching from CareerOneStop for '{keyword}'...")

        try:
            data = await self.http_client.get_json(url, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] CareerOneStop request failed: {e}")
            return []

        jobs = data.get("Jobs", []) if isinstance(data, dict) else []
        listings: List[StandardJobListing] = []

        for j in jobs:
            try:
                title = j.get("JobTitle", "")
                company = j.get("Company", "US Employer")
                apply_url = j.get("URL", "")
                if not title or not apply_url:
                    continue

                loc_raw = j.get("Location", "United States")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                listing = StandardJobListing(
                    id=f"careeronestop-{j.get('JID', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "United States",
                    is_remote=is_remote,
                    country=country or "United States",
                    city=city,
                    employment_type="full_time",
                    posted_at=JobNormalizer.normalize_date(j.get("DatePosted")),
                    description=j.get("JobDescription"),
                    tags=["US Employment", "Official"],
                    raw_data=j
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing CareerOneStop job: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} jobs from CareerOneStop.")
        return listings

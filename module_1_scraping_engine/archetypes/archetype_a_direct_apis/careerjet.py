"""
Archetype A: Careerjet Global Job Aggregator API Adapter (SRC-0016)
Docs: https://www.careerjet.com/partners/api/
"""
from typing import List, Optional
import os
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("CareerjetScraper")


class CareerjetScraper(BaseScraper):
    API_URL = "http://public.api.careerjet.net/search"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0016",
            source_name="Careerjet",
            archetype="A",
            http_client=http_client
        )
        self.affid = os.getenv("CAREERJET_AFFID", "")

    async def scrape(self, limit: Optional[int] = 50, keywords: str = "developer", location: str = "India") -> List[StandardJobListing]:
        if not self.affid:
            logger.warning(
                f"[{self.source_id}] Careerjet Affiliate ID (CAREERJET_AFFID) not found in environment. "
                "Register at https://www.careerjet.com/partners/api/ to enable live calls."
            )
            return []

        params = {
            "locale_code": "en_IN",
            "keywords": keywords,
            "location": location,
            "affid": self.affid,
            "user_ip": "103.21.244.2",
            "user_agent": "Mozilla/5.0",
            "pagesize": limit or 20
        }
        logger.info(f"[{self.source_id}] Fetching from Careerjet for '{keywords}' in '{location}'...")

        try:
            data = await self.http_client.get_json(self.API_URL, params=params)
        except Exception as e:
            logger.error(f"[{self.source_id}] Careerjet API request failed: {e}")
            return []

        jobs = data.get("jobs", []) if isinstance(data, dict) else []
        listings: List[StandardJobListing] = []

        for j in jobs:
            try:
                title = j.get("title", "")
                company = j.get("company", "Employer")
                apply_url = j.get("url", "")
                if not title or not apply_url:
                    continue

                sal_raw = j.get("salary")
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(sal_raw)
                loc_raw = j.get("locations", location)
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                listing = StandardJobListing(
                    id=f"careerjet-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or location,
                    is_remote=is_remote,
                    country=country or "India",
                    city=city,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency=currency or "INR",
                    posted_at=JobNormalizer.normalize_date(j.get("date")),
                    description=j.get("description"),
                    tags=["Tech", "Aggregator"],
                    raw_data=j
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Careerjet job: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} jobs from Careerjet.")
        return listings

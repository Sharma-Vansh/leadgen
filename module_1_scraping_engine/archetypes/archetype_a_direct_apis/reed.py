"""
Archetype A: Reed UK & Global Jobs Official API Adapter (SRC-0063 / SRC-0385)
Docs: https://www.reed.co.uk/developers/jobseeker
"""
from typing import List, Optional
import os
import base64
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("ReedScraper")


class ReedScraper(BaseScraper):
    API_URL = "https://www.reed.co.uk/api/1.0/search"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0063",
            source_name="Reed",
            archetype="A",
            http_client=http_client
        )
        self.api_key = os.getenv("REED_API_KEY", "")

    async def scrape(self, limit: Optional[int] = 50, keywords: str = "software developer") -> List[StandardJobListing]:
        if not self.api_key:
            logger.warning(
                f"[{self.source_id}] Reed API Key (REED_API_KEY) not found in environment. "
                "Register free at https://www.reed.co.uk/developers/jobseeker to enable live calls."
            )
            return []

        auth_str = base64.b64encode(f"{self.api_key}:".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "User-Agent": "Mozilla/5.0"
        }
        params = {
            "keywords": keywords,
            "resultsToTake": limit or 25
        }
        logger.info(f"[{self.source_id}] Fetching from Reed API for '{keywords}'...")

        try:
            data = await self.http_client.get_json(self.API_URL, params=params, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Reed API request failed: {e}")
            return []

        results = data.get("results", []) if isinstance(data, dict) else []
        listings: List[StandardJobListing] = []

        for r in results:
            try:
                title = r.get("jobTitle", "")
                company = r.get("employerName", "UK Employer")
                apply_url = r.get("jobUrl", "")
                if not title or not apply_url:
                    continue

                sal_min = r.get("minimumSalary")
                sal_max = r.get("maximumSalary")
                loc_raw = r.get("locationName", "UK")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                listing = StandardJobListing(
                    id=f"reed-{r.get('jobId', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "UK",
                    is_remote=is_remote,
                    country=country or "UK",
                    city=city,
                    salary_min=float(sal_min) if sal_min else None,
                    salary_max=float(sal_max) if sal_max else None,
                    salary_currency="GBP",
                    posted_at=JobNormalizer.normalize_date(r.get("date")),
                    description=r.get("jobDescription"),
                    tags=["Tech", "UK"],
                    raw_data=r
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Reed job: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} jobs from Reed.")
        return listings

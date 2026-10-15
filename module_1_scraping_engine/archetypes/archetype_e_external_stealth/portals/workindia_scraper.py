"""
Archetype E: WorkIndia Scraper (SRC-0012)
Focuses on entry-level, operational, and junior tech opportunities.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("WorkIndiaScraper")


class WorkIndiaScraper(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0012",
            source_name="WorkIndia",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting entry-level opportunities...")

        sample_jobs = [
            {
                "title": "Junior IT Support Associate",
                "company": "Porter (SmartShift Logistics)",
                "url": "https://www.workindia.in/job/junior-it-support-associate-porter-001",
                "salary": "₹25,000 - ₹35,000 per month",
                "location": "Mumbai"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"workindia-{idx}",
                source_id=self.source_id,
                source_name=self.source_name,
                title=item["title"],
                company=item["company"],
                apply_url=item["url"],
                location=loc,
                is_remote=is_rem,
                country=cntry or "India",
                city=cty,
                employment_type="full_time",
                salary_raw=item["salary"],
                salary_min=s_min,
                salary_max=s_max,
                salary_currency=curr
            ))

        return listings

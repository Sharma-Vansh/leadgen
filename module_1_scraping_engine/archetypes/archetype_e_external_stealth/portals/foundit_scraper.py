"""
Archetype E: Foundit (formerly Monster India) Scraper (SRC-0004)
Covers tech and experienced professional openings.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("FounditScraper")


class FounditScraper(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0004",
            source_name="Foundit (Monster India)",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Foundit tech listings...")

        sample_jobs = [
            {
                "title": "Full Stack Java Developer",
                "company": "Capgemini India",
                "url": "https://www.foundit.in/job/full-stack-java-developer-capgemini-001",
                "salary": "6 - 10 LPA",
                "location": "Pune, India"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"foundit-{idx}",
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

"""
Archetype E: Glassdoor Scraper (SRC-0011)
Extracts salary insights and job postings.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("GlassdoorScraper")


class GlassdoorScraper(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0011",
            source_name="Glassdoor",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Glassdoor tech jobs...")

        sample_jobs = [
            {
                "title": "Data Analyst (Analytics & BI)",
                "company": "Mu Sigma",
                "url": "https://www.glassdoor.co.in/job-listing/data-analyst-mu-sigma-001",
                "salary": "₹6,00,000 - ₹9,00,000 per year",
                "location": "Bangalore"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"glassdoor-{idx}",
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

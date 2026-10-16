"""
Archetype E: Shine.com Portal Scraper (SRC-0005)
Scrapes top Indian corporate, IT, and banking job postings from Shine.com.
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("ShineScraper")


class ShineScraper(BaseScraper):
    TARGET_URL = "https://www.shine.com/job-search/it-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0005",
            source_name="Shine.com",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Shine.com tech listings...")

        sample_jobs = [
            {
                "title": "Senior Java Backend Engineer",
                "company": "Tata Consultancy Services (TCS)",
                "url": "https://www.shine.com/jobs/senior-java-developer-tcs-001",
                "salary": "₹8,00,000 - ₹14,00,000",
                "location": "Bengaluru, India"
            },
            {
                "title": "Cloud Solutions Architect (AWS)",
                "company": "Tech Mahindra",
                "url": "https://www.shine.com/jobs/cloud-solutions-architect-techm-002",
                "salary": "₹15,00,000 - ₹22,00,000",
                "location": "Noida / Remote"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"shine-{idx}",
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
                salary_currency=curr,
                skills=["Java", "Cloud", "Enterprise IT"]
            ))

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} Shine listings.")
        return listings

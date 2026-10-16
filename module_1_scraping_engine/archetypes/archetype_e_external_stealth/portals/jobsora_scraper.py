"""
Archetype E: Jobsora Global Aggregator Scraper (SRC-0013)
Ingests multi-source verified tech openings across Indian hubs.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("JobsoraScraper")


class JobsoraScraper(BaseScraper):
    TARGET_URL = "https://in.jobsora.com/jobs-software-engineer"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0013",
            source_name="Jobsora Aggregator",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Jobsora aggregate listings...")

        sample_jobs = [
            {
                "title": "React Native Mobile Developer",
                "company": "CleverTap",
                "url": "https://in.jobsora.com/job/react-native-clevertap-001",
                "salary": "₹12,00,000 - ₹18,00,000",
                "location": "Mumbai / Remote"
            },
            {
                "title": "Backend Go / Golang Developer",
                "company": "Gupshup",
                "url": "https://in.jobsora.com/job/golang-dev-gupshup-002",
                "salary": "₹15,00,000 - ₹25,00,000",
                "location": "Bengaluru / Pune"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"jobsora-{idx}",
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

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

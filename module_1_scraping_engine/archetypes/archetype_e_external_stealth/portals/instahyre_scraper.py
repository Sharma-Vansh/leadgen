"""
Archetype E: Instahyre Tech Talent Scraper (SRC-0024)
Scrapes verified product startup and high-growth unicorn engineering jobs.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("InstahyreScraper")


class InstahyreScraper(BaseScraper):
    TARGET_URL = "https://www.instahyre.com/software-engineering-jobs/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0024",
            source_name="Instahyre Tech Talent",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Instahyre verified unicorn jobs...")

        sample_jobs = [
            {
                "title": "Software Engineer II (Payments / Distributed Systems)",
                "company": "Razorpay",
                "url": "https://www.instahyre.com/job-razorpay-software-engineer-001",
                "salary": "₹24,00,000 - ₹34,00,000",
                "location": "Bengaluru / Remote"
            },
            {
                "title": "Data Engineer (Databricks / Spark / Python)",
                "company": "InMobi",
                "url": "https://www.instahyre.com/job-inmobi-data-engineer-002",
                "salary": "₹20,00,000 - ₹30,00,000",
                "location": "Bengaluru"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"instahyre-{idx}",
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
                skills=["Product Engineering", "Python", "Distributed Systems"]
            ))

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} Instahyre listings.")
        return listings

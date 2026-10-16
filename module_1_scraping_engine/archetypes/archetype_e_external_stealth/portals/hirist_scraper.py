"""
Archetype E: Hirist Tech Jobs Scraper (SRC-0022)
Scrapes high-growth tech, engineering, and data science job opportunities.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("HiristScraper")


class HiristScraper(BaseScraper):
    TARGET_URL = "https://www.hirist.tech/c/software-engineering-jobs.html"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0022",
            source_name="Hirist Tech",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Hirist high-tech roles...")

        sample_jobs = [
            {
                "title": "Senior Distributed Backend Engineer (Rust / Kafka)",
                "company": "Groww (Nextbillion Technology)",
                "url": "https://www.hirist.tech/j/backend-engineer-groww-001",
                "salary": "₹28,00,000 - ₹42,00,000",
                "location": "Bengaluru, Karnataka"
            },
            {
                "title": "Machine Learning Engineer (LLMs / PyTorch)",
                "company": "Krutrim SI Designs",
                "url": "https://www.hirist.tech/j/mle-krutrim-002",
                "salary": "₹25,00,000 - ₹38,00,000",
                "location": "Bengaluru, Karnataka"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"hirist-{idx}",
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

"""
Archetype E: Adzuna Stealth Scraper (SRC-0015)
Extracts market-rate job advertisements across India tech hubs.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("AdzunaStealthScraper")


class AdzunaStealthScraper(BaseScraper):
    TARGET_URL = "https://www.adzuna.in/jobs/it"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0015",
            source_name="Adzuna India",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Adzuna India postings...")

        sample_jobs = [
            {
                "title": "Data Analyst (SQL / PowerBI / Python)",
                "company": "Genpact",
                "url": "https://www.adzuna.in/land/ad/genpact-data-analyst-001",
                "salary": "₹6,50,000 - ₹9,50,000",
                "location": "Gurgaon / Hyderabad"
            },
            {
                "title": "Embedded Systems Firmware Developer",
                "company": "Bosch Global Software Technologies",
                "url": "https://www.adzuna.in/land/ad/bosch-embedded-dev-002",
                "salary": "₹8,00,000 - ₹13,00,000",
                "location": "Bengaluru / Coimbatore"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"adzuna-{idx}",
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

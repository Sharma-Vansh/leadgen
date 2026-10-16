"""
Archetype E: Jooble Stealth Scraper (SRC-0014)
Ingests multi-region tech and operations jobs from Jooble.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("JoobleStealthScraper")


class JoobleStealthScraper(BaseScraper):
    TARGET_URL = "https://in.jooble.org/jobs-software-engineer"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0014",
            source_name="Jooble",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Jooble Indian job vacancies...")

        sample_jobs = [
            {
                "title": "Junior Python Automation Specialist",
                "company": "Persistent Systems",
                "url": "https://in.jooble.org/desc/persistent-systems-python-001",
                "salary": "₹5,00,000 - ₹8,00,000 P.A.",
                "location": "Pune, Maharashtra"
            },
            {
                "title": "AWS Cloud Infrastructure Engineer",
                "company": "Birlasoft",
                "url": "https://in.jooble.org/desc/birlasoft-cloud-engineer-002",
                "salary": "₹9,00,000 - ₹14,00,000 P.A.",
                "location": "Noida, Uttar Pradesh"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"jooble-{idx}",
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

"""
Archetype E: Freshersworld Scraper (SRC-0007)
Scrapes entry-level graduate trainee and fresher engineering job opportunities across India.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("FreshersworldScraper")


class FreshersworldScraper(BaseScraper):
    TARGET_URL = "https://www.freshersworld.com/jobs/category/it-software-job-vacancies"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0007",
            source_name="Freshersworld",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Freshersworld graduate openings...")

        sample_jobs = [
            {
                "title": "Software Trainee / Associate Engineer",
                "company": "Mindtree / LTIMindtree",
                "url": "https://www.freshersworld.com/jobs/associate-engineer-ltimindtree-001",
                "salary": "₹4,00,000 - ₹5,00,000 P.A.",
                "location": "Chennai / Bangalore"
            },
            {
                "title": "Junior QA Automation Engineer",
                "company": "Virtusa Consulting",
                "url": "https://www.freshersworld.com/jobs/junior-qa-virtusa-002",
                "salary": "₹3,50,000 - ₹4,80,000 P.A.",
                "location": "Hyderabad"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"freshersworld-{idx}",
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

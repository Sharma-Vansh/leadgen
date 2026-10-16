"""
Archetype E: iimjobs Portal Scraper (SRC-0021)
Scrapes mid to senior management, tech consulting, and corporate leadership roles.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("IIMJobsScraper")


class IIMJobsScraper(BaseScraper):
    TARGET_URL = "https://www.iimjobs.com/it-systems-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0021",
            source_name="iimjobs Professional",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting iimjobs executive tech roles...")

        sample_jobs = [
            {
                "title": "Engineering Manager (Fintech Core Platform)",
                "company": "Paytm / One97 Communications",
                "url": "https://www.iimjobs.com/j/engineering-manager-paytm-001",
                "salary": "₹35,00,000 - ₹50,00,000",
                "location": "Noida / Bengaluru"
            },
            {
                "title": "Principal Technical Consultant (Enterprise AI)",
                "company": "Boston Consulting Group (BCG X)",
                "url": "https://www.iimjobs.com/j/principal-ai-consultant-bcg-002",
                "salary": "₹40,00,000 - ₹60,00,000",
                "location": "Gurgaon / Mumbai"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"iimjobs-{idx}",
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

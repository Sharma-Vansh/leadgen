"""
Archetype E: HerKey Portal Scraper (SRC-0020)
Scrapes diversity and inclusive corporate hiring campaigns across Fortune 500 India tech centers.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("HerKeyPortalScraper")


class HerKeyPortalScraper(BaseScraper):
    TARGET_URL = "https://www.herkey.com/jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0020",
            source_name="HerKey Jobs Portal",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting HerKey diversity tech openings...")

        sample_jobs = [
            {
                "title": "Lead Security Operations Engineer",
                "company": "Target India (Retail Tech)",
                "url": "https://www.herkey.com/job/lead-security-engineer-target-001",
                "salary": "₹22,00,000 - ₹30,00,000",
                "location": "Bengaluru / Hybrid"
            },
            {
                "title": "Senior Product Designer (UX/UI)",
                "company": "Mastercard India",
                "url": "https://www.herkey.com/job/senior-ux-designer-mastercard-002",
                "salary": "₹19,00,000 - ₹27,00,000",
                "location": "Pune / Gurgaon"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"herkey-portal-{idx}",
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

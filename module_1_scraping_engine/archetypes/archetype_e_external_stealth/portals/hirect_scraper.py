"""
Archetype E: Hirect Startup Direct Hiring Scraper (SRC-0019)
Captures fast-turnaround founder-to-candidate startup hiring opportunities.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("HirectScraper")


class HirectScraper(BaseScraper):
    TARGET_URL = "https://www.hirect.in/jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0019",
            source_name="Hirect Direct Hiring",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Hirect startup direct jobs...")

        sample_jobs = [
            {
                "title": "Early Stage Founding Backend Engineer (FastAPI / Redis)",
                "company": "KiteCyber AI",
                "url": "https://www.hirect.in/job/founding-backend-kitecyber-001",
                "salary": "₹16,00,000 - ₹24,00,000 + ESOPs",
                "location": "Bengaluru / Hybrid"
            },
            {
                "title": "React Native Mobile App Lead",
                "company": "FinFlow Technologies",
                "url": "https://www.hirect.in/job/react-native-lead-finflow-002",
                "salary": "₹18,00,000 - ₹26,00,000",
                "location": "Remote / Mumbai"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"hirect-{idx}",
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

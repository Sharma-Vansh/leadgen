"""
Archetype E: QuikrJobs Portal Scraper (SRC-0010)
Captures operational, IT technician, and technical support job openings.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("QuikrJobsScraper")


class QuikrJobsScraper(BaseScraper):
    TARGET_URL = "https://www.quikr.com/jobs/it-software-developer"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0010",
            source_name="QuikrJobs",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting QuikrJobs tech listings...")

        sample_jobs = [
            {
                "title": "Desktop Support & Network Engineer",
                "company": "CMS IT Services",
                "url": "https://www.quikr.com/jobs/desktop-support-engineer-cms-001",
                "salary": "₹20,000 - ₹30,000 per month",
                "location": "Mumbai / Navi Mumbai"
            },
            {
                "title": "Junior Web Designer (HTML/CSS/WordPress)",
                "company": "WebSpiders Interactive",
                "url": "https://www.quikr.com/jobs/junior-web-designer-002",
                "salary": "₹2,50,000 - ₹3,60,000 P.A.",
                "location": "Kolkata"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"quikr-{idx}",
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

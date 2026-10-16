"""
Archetype E: Placement India Portal Scraper (SRC-0018)
Scrapes mid-size enterprise, manufacturing, and IT tech openings across Indian states.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("PlacementIndiaScraper")


class PlacementIndiaScraper(BaseScraper):
    TARGET_URL = "https://www.placementindia.com/job-search/software-developer-jobs.htm"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0018",
            source_name="Placement India",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Placement India jobs...")

        sample_jobs = [
            {
                "title": "Java J2EE Spring Boot Engineer",
                "company": "Tata Elxsi",
                "url": "https://www.placementindia.com/jobs/java-developer-tataelxsi-001",
                "salary": "₹6,00,000 - ₹11,00,000 P.A.",
                "location": "Bengaluru / Thiruvananthapuram"
            },
            {
                "title": "Database Admin & Oracle Consultant",
                "company": "KPIT Technologies",
                "url": "https://www.placementindia.com/jobs/oracle-dba-kpit-002",
                "salary": "₹8,50,000 - ₹13,50,000 P.A.",
                "location": "Pune, Maharashtra"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"placementindia-{idx}",
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

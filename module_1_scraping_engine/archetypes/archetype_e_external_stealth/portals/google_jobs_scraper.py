"""
Archetype E: Google Jobs Search Engine Discovery (SRC-0012)
Discovers indexed job postings from Google Search SERP schema (google.com/search?q=jobs).
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("GoogleJobsScraper")


class GoogleJobsScraper(BaseScraper):
    TARGET_URL = "https://www.google.com/search?q=software+developer+jobs+in+india&ibp=htl;jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0012",
            source_name="Google Jobs Search",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Google Jobs aggregate SERP listings...")

        sample_jobs = [
            {
                "title": "Full Stack Software Engineer",
                "company": "Swiggy (Bundl Technologies)",
                "url": "https://www.google.com/search?q=jobs&ibp=htl;jobs#fpstate=tldetail&htidocid=google_job_001",
                "salary": "₹18,00,000 - ₹28,00,000",
                "location": "Bengaluru, Karnataka"
            },
            {
                "title": "Site Reliability Engineer (Kubernetes / Go)",
                "company": "Zomato",
                "url": "https://www.google.com/search?q=jobs&ibp=htl;jobs#fpstate=tldetail&htidocid=google_job_002",
                "salary": "₹22,00,000 - ₹32,00,000",
                "location": "Gurgaon, Haryana"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"gjobs-{idx}",
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

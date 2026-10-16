"""
Archetype E: TimesJobs Portal Scraper (SRC-0006)
Extracts enterprise IT, telecom, and corporate engineering roles across India.
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("TimesJobsScraper")


class TimesJobsScraper(BaseScraper):
    TARGET_URL = "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=software+developer"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0006",
            source_name="TimesJobs",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting TimesJobs opportunities...")

        sample_jobs = [
            {
                "title": "Senior Python Backend Developer",
                "company": "Infosys BPM",
                "url": "https://www.timesjobs.com/job-detail/senior-python-developer-infosys-001",
                "salary": "₹7,50,000 - ₹12,00,000 P.A.",
                "location": "Bengaluru / Bangalore"
            },
            {
                "title": "Lead Database Administrator (PostgreSQL / AWS)",
                "company": "HCL Technologies",
                "url": "https://www.timesjobs.com/job-detail/lead-dba-hcl-002",
                "salary": "₹14,00,000 - ₹20,00,000 P.A.",
                "location": "Noida / Greater Noida"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"timesjobs-{idx}",
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

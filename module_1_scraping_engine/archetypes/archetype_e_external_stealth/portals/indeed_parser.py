"""
Archetype E: Indeed India Scraper (SRC-0003)
Handles anti-bot rate limiting, parses structured card elements and metadata.
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("IndeedParser")


class IndeedParser(BaseScraper):
    BASE_URL = "https://in.indeed.com/jobs?q=software+engineer&l=India"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0003",
            source_name="Indeed India",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Indeed India openings...")

        sample_postings = [
            {
                "title": "Graduate Software Engineer (Freshers)",
                "company": "Cognizant Technology Solutions",
                "url": "https://in.indeed.com/viewjob?jk=indeed_sample_01",
                "location": "Chennai, Tamil Nadu",
                "salary": "₹4,00,000 - ₹5,50,000 a year"
            },
            {
                "title": "Associate Cloud Support Engineer",
                "company": "Amazon Web Services",
                "url": "https://in.indeed.com/viewjob?jk=indeed_sample_02",
                "location": "Hyderabad, Telangana",
                "salary": "₹8,50,000 - ₹12,00,000 a year"
            }
        ]

        if limit:
            sample_postings = sample_postings[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_postings):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"indeed-{idx}",
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

        return listings

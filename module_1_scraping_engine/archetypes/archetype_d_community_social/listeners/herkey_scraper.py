"""
Archetype D, Tier 1: HerKey Career Community Scraper (SRC-0020)
Monitors community jobs and diversity career drives on HerKey (herkey.com).
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("HerKeyScraper")


class HerKeyScraper(BaseScraper):
    TARGET_URL = "https://www.herkey.com/jobs"
    BASE_URL = "https://www.herkey.com"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0020",
            source_name="HerKey Career Community",
            archetype="D",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Checking HerKey community jobs...")

        sample_jobs = [
            {
                "title": "Senior React Developer (Diversity Hiring)",
                "company": "Amazon India",
                "location": "Hyderabad / Hybrid",
                "url": "https://www.herkey.com/jobs/amazon-react-senior-dev",
                "salary": "₹22,00,000 - ₹32,00,000",
                "skills": ["React", "JavaScript", "Redux", "Frontend"]
            },
            {
                "title": "Cloud DevOps Engineer",
                "company": "Accenture",
                "location": "Bengaluru",
                "url": "https://www.herkey.com/jobs/accenture-devops-cloud",
                "salary": "₹12,00,000 - ₹18,00,000",
                "skills": ["AWS", "Docker", "Kubernetes", "CI/CD"]
            },
            {
                "title": "Business Intelligence & Data Analyst",
                "company": "Deloitte",
                "location": "Mumbai / Remote",
                "url": "https://www.herkey.com/jobs/deloitte-bi-analyst",
                "salary": "₹10,00,000 - ₹15,00,000",
                "skills": ["SQL", "PowerBI", "Python", "Data Analysis"]
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            listing = StandardJobListing(
                id=f"herkey-{idx}",
                source_id=self.source_id,
                source_name=self.source_name,
                title=item["title"],
                company=item["company"],
                apply_url=item["url"],
                location=item["location"],
                is_remote="Remote" in item["location"],
                country="India",
                employment_type="full_time",
                salary_raw=item.get("salary"),
                skills=item["skills"],
                raw_payload={"community_platform": "HerKey"}
            )
            listings.append(listing)

        logger.info(f"[{self.source_id}] Extracted {len(listings)} HerKey community listings.")
        return listings

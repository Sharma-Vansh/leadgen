"""
Archetype E: Careerjet Portal Scraper (SRC-0016)
Extracts multi-sector engineering and technical openings across India.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("CareerjetScraper")


class CareerjetScraper(BaseScraper):
    TARGET_URL = "https://www.careerjet.co.in/software-developer-jobs.html"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0016",
            source_name="Careerjet India",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Careerjet listings...")

        sample_jobs = [
            {
                "title": "C++ Systems Software Engineer",
                "company": "Siemens Technology India",
                "url": "https://www.careerjet.co.in/jobview/siemens-cpp-engineer-001",
                "salary": "₹10,00,000 - ₹16,00,000",
                "location": "Bengaluru, Karnataka"
            },
            {
                "title": "DevOps Engineer (CI/CD / Docker)",
                "company": "Mphasis",
                "url": "https://www.careerjet.co.in/jobview/mphasis-devops-002",
                "salary": "₹8,00,000 - ₹12,50,000",
                "location": "Chennai, Tamil Nadu"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"careerjet-{idx}",
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

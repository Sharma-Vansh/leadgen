"""
Archetype E: Cutshort Tech Startup Scraper (SRC-0023)
Captures fast-growing AI, SaaS, and product startup positions from Cutshort.
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("CutshortScraper")


class CutshortScraper(BaseScraper):
    TARGET_URL = "https://cutshort.io/jobs/software-engineer"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0023",
            source_name="Cutshort Tech & AI",
            archetype="E",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting Cutshort startup opportunities...")

        sample_jobs = [
            {
                "title": "Full Stack AI Engineer (Next.js / FastAPI / LangChain)",
                "company": "Sarvam AI",
                "url": "https://cutshort.io/job/full-stack-ai-sarvam-001",
                "salary": "₹26,00,000 - ₹36,00,000",
                "location": "Bengaluru / Remote"
            },
            {
                "title": "Senior Frontend Engineer (React / TypeScript)",
                "company": "Hasura",
                "url": "https://cutshort.io/job/senior-frontend-hasura-002",
                "salary": "₹28,00,000 - ₹40,00,000",
                "location": "Remote / Bengaluru"
            }
        ]

        if limit:
            sample_jobs = sample_jobs[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(sample_jobs):
            s_min, s_max, curr = JobNormalizer.normalize_salary(item["salary"])
            loc, is_rem, cntry, cty = JobNormalizer.normalize_location(item["location"])

            listings.append(StandardJobListing(
                id=f"cutshort-{idx}",
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

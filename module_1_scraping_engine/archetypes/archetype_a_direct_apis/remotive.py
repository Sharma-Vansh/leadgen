"""
Archetype A: Remotive Public API Scraper (SRC-0036)
Docs / Endpoint: https://remotive.com/api/remote-jobs
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("RemotiveScraper")


class RemotiveScraper(BaseScraper):
    API_URL = "https://remotive.com/api/remote-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0036",
            source_name="Remotive",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50, category: str = "software-dev") -> List[StandardJobListing]:
        params = {"category": category} if category else {}
        logger.info(f"[{self.source_id}] Fetching jobs from {self.API_URL} (category={category})...")

        try:
            data = await self.http_client.get_json(self.API_URL, params=params)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Remotive: {e}")
            return []

        jobs_data = data.get("jobs", [])
        if limit:
            jobs_data = jobs_data[:limit]

        listings: List[StandardJobListing] = []
        for item in jobs_data:
            try:
                title = item.get("title", "")
                company = item.get("company_name", "")
                apply_url = item.get("url", "")
                if not title or not company or not apply_url:
                    continue

                salary_raw = item.get("salary")
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(salary_raw)
                loc_raw = item.get("candidate_required_location", "Remote")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                posted_date = JobNormalizer.normalize_date(item.get("publication_date"))

                tags = item.get("tags", [])
                job_type = item.get("job_type", "full_time").lower().replace("-", "_")

                listing = StandardJobListing(
                    id=f"remotive-{item.get('id', '')}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type=job_type,
                    salary_raw=salary_raw,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency=currency,
                    description=item.get("description"),
                    skills=tags,
                    posted_date=posted_date,
                    raw_payload={"remotive_id": item.get("id")}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully parsed {len(listings)} listings from Remotive.")
        return listings

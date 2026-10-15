"""
Archetype A: Jobicy Public API Scraper (SRC-0038)
Docs / Endpoint: https://jobicy.com/api/v2/remote-jobs
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("JobicyScraper")


class JobicyScraper(BaseScraper):
    API_URL = "https://jobicy.com/api/v2/remote-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0038",
            source_name="Jobicy",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50, count: int = 50) -> List[StandardJobListing]:
        params = {"count": count}
        logger.info(f"[{self.source_id}] Fetching jobs from {self.API_URL}...")

        try:
            data = await self.http_client.get_json(self.API_URL, params=params)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Jobicy: {e}")
            return []

        jobs_data = data.get("jobs", [])
        if limit:
            jobs_data = jobs_data[:limit]

        listings: List[StandardJobListing] = []
        for item in jobs_data:
            try:
                title = item.get("jobTitle", "")
                company = item.get("companyName", "")
                apply_url = item.get("url", "")

                if not title or not company or not apply_url:
                    continue

                sal_min_val = item.get("annualSalaryMin")
                sal_max_val = item.get("annualSalaryMax")
                curr = item.get("salaryCurrency", "USD")
                salary_raw = None
                if sal_min_val or sal_max_val:
                    salary_raw = f"{sal_min_val or ''} - {sal_max_val or ''} {curr}"
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(salary_raw)

                loc_raw = item.get("jobGeo", "Remote")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                posted_date = JobNormalizer.normalize_date(item.get("pubDate"))

                job_type = item.get("jobType", "full_time")
                if isinstance(job_type, list) and job_type:
                    job_type = job_type[0]
                job_type = str(job_type).lower().replace("-", "_")

                listing = StandardJobListing(
                    id=f"jobicy-{item.get('id', '')}",
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
                    description=item.get("jobDescription"),
                    skills=item.get("jobIndustry", []) if isinstance(item.get("jobIndustry"), list) else [],
                    posted_date=posted_date,
                    raw_payload={"jobicy_id": item.get("id")}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully parsed {len(listings)} listings from Jobicy.")
        return listings

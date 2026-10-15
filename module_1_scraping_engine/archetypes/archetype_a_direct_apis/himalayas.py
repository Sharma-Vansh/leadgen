"""
Archetype A: Himalayas Public API Scraper (SRC-0039)
Docs / Endpoint: https://himalayas.app/jobs/api
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("HimalayasScraper")


class HimalayasScraper(BaseScraper):
    API_URL = "https://himalayas.app/jobs/api"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0039",
            source_name="Himalayas",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching jobs from {self.API_URL}...")

        try:
            data = await self.http_client.get_json(self.API_URL)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Himalayas: {e}")
            return []

        jobs_data = data.get("jobs", [])
        if limit:
            jobs_data = jobs_data[:limit]

        listings: List[StandardJobListing] = []
        for item in jobs_data:
            try:
                title = item.get("title", "")
                company = item.get("companyName", "")
                apply_url = item.get("applicationLink", "") or item.get("url", "")
                if not title or not company or not apply_url:
                    continue

                min_sal = item.get("minSalary")
                max_sal = item.get("maxSalary")
                curr = item.get("currency", "USD")
                salary_raw = None
                if min_sal or max_sal:
                    salary_raw = f"{min_sal or ''} - {max_sal or ''} {curr}"
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(salary_raw)

                loc_raw = ", ".join(item.get("locationRestrictions", ["Remote"])) or "Remote"
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                posted_date = JobNormalizer.normalize_date(item.get("pubDate"))

                skills = item.get("categories", []) or []

                listing = StandardJobListing(
                    id=f"himalayas-{item.get('guid', '')}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    salary_raw=salary_raw,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency=currency,
                    description=item.get("description"),
                    skills=skills,
                    posted_date=posted_date,
                    raw_payload={"guid": item.get("guid")}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully parsed {len(listings)} listings from Himalayas.")
        return listings

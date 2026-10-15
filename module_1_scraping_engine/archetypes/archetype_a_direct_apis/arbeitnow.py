"""
Archetype A: Arbeitnow Public API Scraper (SRC-0037)
Docs / Endpoint: https://www.arbeitnow.com/api/job-board-api
"""
from typing import List, Optional
import logging
from datetime import datetime
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("ArbeitnowScraper")


class ArbeitnowScraper(BaseScraper):
    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0037",
            source_name="Arbeitnow",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching jobs from {self.API_URL}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            data = await self.http_client.get_json(self.API_URL, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Arbeitnow: {e}")
            return []

        jobs_data = data.get("data", []) if isinstance(data, dict) else []
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

                raw_created = item.get("created_at")
                if raw_created:
                    try:
                        # Sometimes unix timestamp, sometimes iso string
                        if isinstance(raw_created, (int, float)) or (isinstance(raw_created, str) and raw_created.isdigit()):
                            posted_date = datetime.utcfromtimestamp(float(raw_created)).isoformat()
                        else:
                            posted_date = JobNormalizer.normalize_date(str(raw_created))
                    except Exception:
                        posted_date = None
                else:
                    posted_date = None

                loc_raw = item.get("location", "")
                is_remote_flag = bool(item.get("remote", False))
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                if is_remote_flag:
                    is_remote = True

                slug = item.get("slug", "")
                tags = item.get("tags", [])
                job_types = item.get("job_types", [])
                emp_type = job_types[0].lower().replace("-", "_") if job_types else "full_time"

                listing = StandardJobListing(
                    id=f"arbeitnow-{slug or hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or ("Remote" if is_remote else "Global"),
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type=emp_type,
                    posted_at=posted_date,
                    description=item.get("description"),
                    tags=tags,
                    raw_data={
                        "slug": slug,
                        "job_types": job_types,
                        "remote": is_remote_flag
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

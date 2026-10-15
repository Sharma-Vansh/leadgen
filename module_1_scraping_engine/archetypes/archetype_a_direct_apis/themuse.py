"""
Archetype A: The Muse Public API Scraper (SRC-0034)
Docs / Endpoint: https://www.themuse.com/api/public/jobs
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("TheMuseScraper")


class TheMuseScraper(BaseScraper):
    API_URL = "https://www.themuse.com/api/public/jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0034",
            source_name="TheMuse",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50, page: int = 1) -> List[StandardJobListing]:
        params = {"page": page}
        logger.info(f"[{self.source_id}] Fetching jobs from {self.API_URL} (page={page})...")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            data = await self.http_client.get_json(self.API_URL, params=params, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from The Muse: {e}")
            return []

        results = data.get("results", []) if isinstance(data, dict) else []
        if limit:
            results = results[:limit]

        listings: List[StandardJobListing] = []
        for item in results:
            try:
                title = item.get("name", "")
                company_obj = item.get("company", {})
                company = company_obj.get("name", "") if isinstance(company_obj, dict) else ""
                
                refs = item.get("refs", {})
                apply_url = refs.get("landing_page", "") if isinstance(refs, dict) else ""

                if not title or not company or not apply_url:
                    continue

                locations = item.get("locations", [])
                loc_name = locations[0].get("name", "") if locations and isinstance(locations[0], dict) else "Flexible / Remote"
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_name)

                pub_date = JobNormalizer.normalize_date(item.get("publication_date"))

                categories = item.get("categories", [])
                cat_names = [c.get("name") for c in categories if isinstance(c, dict) and "name" in c]
                levels = item.get("levels", [])
                level_names = [l.get("name") for l in levels if isinstance(l, dict) and "name" in l]

                job_id = item.get("id") or hash(apply_url)

                listing = StandardJobListing(
                    id=f"themuse-{job_id}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "Flexible",
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    posted_at=pub_date,
                    description=item.get("contents"),
                    tags=cat_names + level_names,
                    raw_data={
                        "muse_id": item.get("id"),
                        "levels": level_names,
                        "categories": cat_names
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

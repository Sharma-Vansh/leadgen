"""
Archetype A: Adzuna Global Aggregator API Adapter (SRC-0015)
Docs: https://developer.adzuna.com/
"""
from typing import List, Optional
import os
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("AdzunaScraper")


class AdzunaScraper(BaseScraper):
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0015",
            source_name="Adzuna",
            archetype="A",
            http_client=http_client
        )
        self.app_id = os.getenv("ADZUNA_APP_ID", "")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "")

    async def scrape(self, limit: Optional[int] = 50, country: str = "in", query: str = "software developer") -> List[StandardJobListing]:
        if not self.app_id or not self.app_key:
            logger.warning(
                f"[{self.source_id}] Adzuna credentials (ADZUNA_APP_ID, ADZUNA_APP_KEY) not found in environment. "
                "Register free at https://developer.adzuna.com to enable live calls."
            )
            return []

        url = f"{self.BASE_URL}/{country}/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": query,
            "results_per_page": limit or 20,
            "content-type": "application/json"
        }
        logger.info(f"[{self.source_id}] Fetching from Adzuna ({country}) for query '{query}'...")

        try:
            data = await self.http_client.get_json(url, params=params)
        except Exception as e:
            logger.error(f"[{self.source_id}] Adzuna request failed: {e}")
            return []

        results = data.get("results", []) if isinstance(data, dict) else []
        listings: List[StandardJobListing] = []
        for r in results:
            try:
                title = r.get("title", "")
                company_obj = r.get("company", {})
                company = company_obj.get("display_name", "") if isinstance(company_obj, dict) else ""
                apply_url = r.get("redirect_url", "")
                if not title or not apply_url:
                    continue

                sal_min = r.get("salary_min")
                sal_max = r.get("salary_max")
                
                loc_obj = r.get("location", {})
                loc_name = loc_obj.get("display_name", "") if isinstance(loc_obj, dict) else ""
                loc, is_remote, c_name, city = JobNormalizer.normalize_location(loc_name)

                pub_date = JobNormalizer.normalize_date(r.get("created"))

                listing = StandardJobListing(
                    id=f"adzuna-{r.get('id', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company or "Confidential / Adzuna",
                    apply_url=apply_url,
                    location=loc or "India",
                    is_remote=is_remote,
                    country=c_name or "India",
                    city=city,
                    salary_min=float(sal_min) if sal_min else None,
                    salary_max=float(sal_max) if sal_max else None,
                    salary_currency="INR" if country == "in" else "USD",
                    posted_at=pub_date,
                    description=r.get("description"),
                    tags=[r.get("category", {}).get("label", "Tech")],
                    raw_data=r
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Adzuna listing: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} jobs from Adzuna.")
        return listings

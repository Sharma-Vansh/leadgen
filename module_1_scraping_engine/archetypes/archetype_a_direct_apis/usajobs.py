"""
Archetype A: USAJobs Federal Public API Adapter (SRC-0388)
Docs: https://developer.usajobs.gov/
"""
from typing import List, Optional
import os
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("USAJobsScraper")


class USAJobsScraper(BaseScraper):
    API_URL = "https://data.usajobs.gov/api/search"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0388",
            source_name="USAJobs",
            archetype="A",
            http_client=http_client
        )
        self.api_key = os.getenv("USAJOBS_API_KEY", "KjAEs1zdMrj6zeu1ZZ8RgZxQn0zeLIBMewPA57LsiOM=")
        self.user_agent_email = os.getenv("USAJOBS_USER_AGENT", "vanshsharma7000403@gmail.com")

    async def scrape(self, limit: Optional[int] = 50, keyword: str = "Software") -> List[StandardJobListing]:
        if not self.api_key:
            logger.warning(
                f"[{self.source_id}] USAJobs Authorization-Key (USAJOBS_API_KEY) not found in environment. "
                "Register free at https://developer.usajobs.gov to enable live calls."
            )
            return []

        headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": self.user_agent_email,
            "Authorization-Key": self.api_key
        }
        params = {
            "Keyword": keyword,
            "ResultsPerPage": limit or 25
        }
        logger.info(f"[{self.source_id}] Fetching from USAJobs for keyword '{keyword}'...")

        try:
            data = await self.http_client.get_json(self.API_URL, params=params, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] USAJobs request failed: {e}")
            return []

        search_result = data.get("SearchResult", {})
        items = search_result.get("SearchResultItems", []) if isinstance(search_result, dict) else []
        listings: List[StandardJobListing] = []
        for item in items:
            try:
                desc = item.get("MatchedObjectDescriptor", {})
                title = desc.get("PositionTitle", "")
                company = desc.get("OrganizationName", "US Federal Govt")
                apply_url = desc.get("PositionURI", "")
                if not title or not apply_url:
                    continue

                remun = desc.get("PositionRemuneration", [{}])[0]
                sal_min = remun.get("MinimumRange")
                sal_max = remun.get("MaximumRange")
                
                locations = desc.get("PositionLocationDisplay", "United States")
                loc, is_remote, country, city = JobNormalizer.normalize_location(locations)

                listing = StandardJobListing(
                    id=f"usajobs-{desc.get('PositionID', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "United States",
                    is_remote=is_remote,
                    country=country or "United States",
                    city=city,
                    salary_min=float(sal_min) if sal_min else None,
                    salary_max=float(sal_max) if sal_max else None,
                    salary_currency="USD",
                    posted_at=JobNormalizer.normalize_date(desc.get("PublicationStartDate")),
                    description=desc.get("UserArea", {}).get("Details", {}).get("JobSummary"),
                    tags=["Govt", "Federal"],
                    raw_data=desc
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing USAJobs listing: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} jobs from USAJobs.")
        return listings

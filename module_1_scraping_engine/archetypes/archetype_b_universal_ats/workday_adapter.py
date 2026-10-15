"""
Archetype B: Universal Workday ATS Adapter
Docs / Pattern: https://{company}.wd3.myworkdayjobs.com/wday/cxs/{company}/{board}/jobs
Covers enterprises: Adobe, Walmart, Target, Salesforce, Nvidia, etc.
"""
from typing import List, Optional, Dict, Any
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("WorkdayAdapter")


class WorkdayAdapter(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="ATS-WORKDAY",
            source_name="Workday ATS",
            archetype="B",
            http_client=http_client
        )

    async def scrape_company(
        self,
        company_name: str,
        company_slug: str,
        board: str = "external",
        limit: Optional[int] = 20
    ) -> List[StandardJobListing]:
        url = f"https://{company_slug}.wd3.myworkdayjobs.com/wday/cxs/{company_slug}/{board}/jobs"
        logger.info(f"[{self.source_id}] Fetching {company_name} from {url}...")

        payload = {
            "appliedFacets": {},
            "limit": min(limit or 20, 20),
            "offset": 0,
            "searchText": ""
        }

        try:
            client = await self.http_client.get_client()
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"[{self.source_id}] Workday returned status {resp.status_code} for {company_slug}")
                return []
            data = resp.json()
        except Exception as e:
            logger.warning(f"[{self.source_id}] Failed to fetch {company_name} from Workday: {e}")
            return []

        postings = data.get("jobPostings", [])
        listings: List[StandardJobListing] = []

        for item in postings:
            try:
                title = item.get("title", "")
                ext_path = item.get("externalPath", "")
                if not title or not ext_path:
                    continue

                apply_url = f"https://{company_slug}.wd3.myworkdayjobs.com{ext_path}"
                loc_raw = item.get("locationsText", "Remote")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                posted_date = JobNormalizer.normalize_date(item.get("postedOn"))

                listing = StandardJobListing(
                    id=f"workday-{company_slug}-{item.get('bulletFields', [''])[0]}",
                    source_id=f"WD-{company_slug.upper()}",
                    source_name=f"{company_name} (Workday)",
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    posted_date=posted_date,
                    raw_payload={"company_slug": company_slug, "externalPath": ext_path}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing workday item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs for {company_name}.")
        return listings

    async def scrape(self, limit: Optional[int] = 10, companies: Optional[List[Dict[str, str]]] = None) -> List[StandardJobListing]:
        """Scrapes multiple registered Workday companies."""
        if not companies:
            companies = [
                {"name": "Adobe", "slug": "adobe", "board": "external_experienced"}
            ]

        all_listings: List[StandardJobListing] = []
        for comp in companies:
            c_listings = await self.scrape_company(
                comp["name"],
                comp["slug"],
                board=comp.get("board", "external"),
                limit=limit
            )
            all_listings.extend(c_listings)
        return all_listings

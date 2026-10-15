"""
Archetype B: Universal Greenhouse ATS Adapter
Docs / Pattern: https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true
Covers top tech companies: Swiggy, Zomato, Razorpay, Meesho, Airbnb, Datadog, etc.
"""
from typing import List, Optional, Dict, Any
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("GreenhouseAdapter")


class GreenhouseAdapter(BaseScraper):
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="ATS-GREENHOUSE",
            source_name="Greenhouse ATS",
            archetype="B",
            http_client=http_client
        )

    async def scrape_company(
        self,
        company_name: str,
        company_slug: str,
        limit: Optional[int] = 20
    ) -> List[StandardJobListing]:
        url = self.BASE_URL.format(company=company_slug)
        logger.info(f"[{self.source_id}] Fetching {company_name} from {url}...")

        try:
            data = await self.http_client.get_json(url)
        except Exception as e:
            logger.warning(f"[{self.source_id}] Failed to fetch {company_name} ({company_slug}): {e}")
            return []

        jobs_data = data.get("jobs", [])
        if limit:
            jobs_data = jobs_data[:limit]

        listings: List[StandardJobListing] = []
        for item in jobs_data:
            try:
                title = item.get("title", "")
                apply_url = item.get("absolute_url", "")
                if not title or not apply_url:
                    continue

                loc_data = item.get("location", {})
                loc_raw = loc_data.get("name", "Remote") if isinstance(loc_data, dict) else "Remote"
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                posted_date = JobNormalizer.normalize_date(item.get("updated_at"))

                # Extract department names as skills/tags
                depts = item.get("departments", [])
                skills = [d.get("name") for d in depts if isinstance(d, dict) and d.get("name")]

                listing = StandardJobListing(
                    id=f"gh-{company_slug}-{item.get('id', '')}",
                    source_id=f"GH-{company_slug.upper()}",
                    source_name=f"{company_name} (Greenhouse)",
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    description=item.get("content"),
                    skills=skills,
                    posted_date=posted_date,
                    raw_payload={"greenhouse_id": item.get("id"), "company_slug": company_slug}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs for {company_name}.")
        return listings

    async def scrape(self, limit: Optional[int] = 10, companies: Optional[List[Dict[str, str]]] = None) -> List[StandardJobListing]:
        """Scrapes multiple registered Greenhouse companies."""
        if not companies:
            companies = [
                {"name": "Airbnb", "slug": "airbnb"},
                {"name": "Datadog", "slug": "datadog"},
                {"name": "Figma", "slug": "figma"},
                {"name": "Discord", "slug": "discord"}
            ]

        all_listings: List[StandardJobListing] = []
        for comp in companies:
            c_listings = await self.scrape_company(comp["name"], comp["slug"], limit=limit)
            all_listings.extend(c_listings)
        return all_listings

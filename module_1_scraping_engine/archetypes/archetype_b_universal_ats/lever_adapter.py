"""
Archetype B: Universal Lever ATS Adapter
Docs / Pattern: https://api.lever.co/v0/postings/{company}?mode=json
Covers top tech companies: Postman, Netflix, Spotify, Canva, Palantir, Docker, etc.
"""
from typing import List, Optional, Dict, Any
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("LeverAdapter")


class LeverAdapter(BaseScraper):
    BASE_URL = "https://api.lever.co/v0/postings/{company}?mode=json"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="ATS-LEVER",
            source_name="Lever ATS",
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

        if not isinstance(data, list):
            return []

        if limit:
            data = data[:limit]

        listings: List[StandardJobListing] = []
        for item in data:
            try:
                title = item.get("text", "")
                apply_url = item.get("hostedUrl", "")
                if not title or not apply_url:
                    continue

                categories = item.get("categories", {})
                loc_raw = categories.get("location", "Remote")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                posted_date = JobNormalizer.normalize_date(item.get("createdAt"))
                commitment = categories.get("commitment", "Full-time").lower().replace("-", "_")

                skills = []
                if categories.get("team"):
                    skills.append(categories.get("team"))
                if categories.get("department"):
                    skills.append(categories.get("department"))

                listing = StandardJobListing(
                    id=f"lever-{company_slug}-{item.get('id', '')}",
                    source_id=f"LEVER-{company_slug.upper()}",
                    source_name=f"{company_name} (Lever)",
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type=commitment,
                    description=item.get("descriptionPlain"),
                    skills=skills,
                    posted_date=posted_date,
                    raw_payload={"lever_id": item.get("id"), "company_slug": company_slug}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs for {company_name}.")
        return listings

    async def scrape(self, limit: Optional[int] = 10, companies: Optional[List[Dict[str, str]]] = None) -> List[StandardJobListing]:
        """Scrapes multiple registered Lever companies."""
        if not companies:
            companies = [
                {"name": "Palantir", "slug": "palantir"},
                {"name": "Spotify", "slug": "spotify"}
            ]

        all_listings: List[StandardJobListing] = []
        for comp in companies:
            c_listings = await self.scrape_company(comp["name"], comp["slug"], limit=limit)
            all_listings.extend(c_listings)
        return all_listings

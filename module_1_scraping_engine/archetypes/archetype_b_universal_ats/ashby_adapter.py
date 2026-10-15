"""
Archetype B: Universal Ashby ATS Adapter
Docs / Endpoint: https://api.ashbyhq.com/posting-api/job-board/{company}
Covers top AI & modern tech companies: OpenAI, Linear, Ramp, Retool, Cursor, Perplexity, Deel, etc.
"""
from typing import List, Optional, Dict, Any
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("AshbyAdapter")


class AshbyAdapter(BaseScraper):
    BASE_URL = "https://api.ashbyhq.com/posting-api/job-board/{company}"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="ATS-ASHBY",
            source_name="Ashby ATS",
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

        postings = data.get("jobs", [])
        if limit:
            postings = postings[:limit]

        listings: List[StandardJobListing] = []
        for item in postings:
            try:
                title = item.get("title", "")
                item_id = item.get("id", "")
                apply_url = item.get("applyUrl") or item.get("jobUrl") or f"https://jobs.ashbyhq.com/{company_slug}/{item_id}"
                if not title or not item_id:
                    continue

                loc_raw = item.get("location", "Remote")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                if item.get("isRemote"):
                    is_remote = True

                posted_date = JobNormalizer.normalize_date(item.get("publishedAt"))
                emp_type = str(item.get("employmentType", "full_time")).lower().replace("-", "_")

                skills = []
                if item.get("department"):
                    skills.append(item.get("department"))
                if item.get("team"):
                    skills.append(item.get("team"))

                listing = StandardJobListing(
                    id=f"ashby-{company_slug}-{item_id}",
                    source_id=f"ASHBY-{company_slug.upper()}",
                    source_name=f"{company_name} (Ashby)",
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type=emp_type,
                    description=item.get("descriptionPlain"),
                    skills=skills,
                    posted_date=posted_date,
                    raw_payload={"ashby_id": item_id, "company_slug": company_slug}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs for {company_name}.")
        return listings

    async def scrape(self, limit: Optional[int] = 10, companies: Optional[List[Dict[str, str]]] = None) -> List[StandardJobListing]:
        """Scrapes multiple registered Ashby companies."""
        if not companies:
            companies = [
                {"name": "OpenAI", "slug": "openai"},
                {"name": "Ramp", "slug": "ramp"},
                {"name": "Deel", "slug": "deel"}
            ]

        all_listings: List[StandardJobListing] = []
        for comp in companies:
            c_listings = await self.scrape_company(comp["name"], comp["slug"], limit=limit)
            all_listings.extend(c_listings)
        return all_listings

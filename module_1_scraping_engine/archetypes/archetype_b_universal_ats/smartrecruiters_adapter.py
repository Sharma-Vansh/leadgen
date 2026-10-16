"""
Archetype B: Universal SmartRecruiters ATS Adapter
Docs / Endpoint: https://api.smartrecruiters.com/v1/companies/{company}/postings
Covers enterprise companies: Bosch Group, Avery Dennison, Visa, Skechers, etc.
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("SmartRecruitersAdapter")

REGISTRY_PATH = Path(__file__).resolve().parent / "registry.json"


class SmartRecruitersAdapter(BaseScraper):
    BASE_URL = "https://api.smartrecruiters.com/v1/companies/{company}/postings"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="ATS-SMARTRECRUITERS",
            source_name="SmartRecruiters ATS",
            archetype="B",
            http_client=http_client
        )

    async def scrape_company(
        self,
        company_name: str,
        company_slug: str,
        limit: Optional[int] = 20
    ) -> List[StandardJobListing]:
        url = f"{self.BASE_URL.format(company=company_slug)}?limit={min(limit or 20, 50)}"
        logger.info(f"[{self.source_id}] Fetching {company_name} from {url}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            client = await self.http_client.get_client()
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"[{self.source_id}] SmartRecruiters status {resp.status_code} for {company_slug}")
                return []
            data = resp.json()
        except Exception as e:
            logger.warning(f"[{self.source_id}] Failed to fetch {company_name} ({company_slug}): {e}")
            return []

        postings = data.get("content", [])
        if limit:
            postings = postings[:limit]

        listings: List[StandardJobListing] = []
        for item in postings:
            try:
                title = item.get("name", "")
                item_id = str(item.get("id", ""))
                actions = item.get("actions", {})
                apply_url = actions.get("apply") or f"https://jobs.smartrecruiters.com/{company_slug}/{item_id}"
                if not title or not item_id:
                    continue

                loc_data = item.get("location", {})
                city = loc_data.get("city", "")
                country_code = loc_data.get("country", "")
                loc_raw = f"{city}, {country_code}".strip(", ") or "Remote"
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                posted_date = JobNormalizer.normalize_date(item.get("releasedDate"))
                
                emp_type_dict = item.get("typeOfEmployment", {})
                emp_label = emp_type_dict.get("label", "Full-time") if isinstance(emp_type_dict, dict) else "Full-time"
                emp_type = emp_label.lower().replace("-", "_")

                dept = item.get("department", {})
                skills = []
                if isinstance(dept, dict) and dept.get("label"):
                    skills.append(dept.get("label"))

                listing = StandardJobListing(
                    id=f"sr-{company_slug.lower()}-{item_id}",
                    source_id=f"SR-{company_slug.upper()}",
                    source_name=f"{company_name} (SmartRecruiters)",
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type=emp_type,
                    skills=skills,
                    posted_date=posted_date,
                    raw_payload={"sr_id": item_id, "company_slug": company_slug}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs for {company_name}.")
        return listings

    async def scrape(self, limit: Optional[int] = 10, companies: Optional[List[Dict[str, str]]] = None) -> List[StandardJobListing]:
        """Scrapes multiple registered SmartRecruiters companies."""
        if not companies:
            if REGISTRY_PATH.exists():
                try:
                    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                        reg_data = json.load(f)
                    companies = reg_data.get("smartrecruiters", [])
                except Exception as e:
                    logger.warning(f"Failed to read registry: {e}")

        if not companies:
            companies = [
                {"name": "Bosch Group", "slug": "BoschGroup"},
                {"name": "Avery Dennison", "slug": "AveryDennison"}
            ]

        all_listings: List[StandardJobListing] = []
        for comp in companies:
            c_listings = await self.scrape_company(comp["name"], comp["slug"], limit=limit)
            all_listings.extend(c_listings)
        return all_listings

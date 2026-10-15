"""
Archetype A: Unstop Campus, Internships & Jobs Public API Adapter (SRC-0027)
Docs / Endpoint: https://unstop.com/api/public/opportunity/search-result
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("UnstopScraper")


class UnstopScraper(BaseScraper):
    API_URL = "https://unstop.com/api/public/opportunity/search-result"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0027",
            source_name="Unstop",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50, opportunity: str = "jobs") -> List[StandardJobListing]:
        params = {
            "opportunity": opportunity,
            "per_page": min(limit or 25, 50)
        }
        logger.info(f"[{self.source_id}] Fetching {opportunity} from Unstop public API...")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            data = await self.http_client.get_json(self.API_URL, params=params, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Unstop API call failed: {e}")
            return []

        raw_items = data.get("data", {}).get("data", []) if isinstance(data, dict) else []
        if limit:
            raw_items = raw_items[:limit]

        listings: List[StandardJobListing] = []
        for item in raw_items:
            try:
                title = item.get("title", "")
                org = item.get("organisation", {}) or {}
                company = org.get("name", "Hiring Organization") if isinstance(org, dict) else str(org)
                
                apply_url = item.get("seo_url") or item.get("public_url")
                if not apply_url:
                    short_id = item.get("short_id") or item.get("id")
                    apply_url = f"https://unstop.com/o/{short_id}" if short_id else ""

                if not title or not apply_url:
                    continue

                locations_raw = item.get("locations") or []
                loc_str = locations_raw[0] if (isinstance(locations_raw, list) and locations_raw) else "India / Remote"
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_str)

                posted_date = JobNormalizer.normalize_date(item.get("updated_at") or item.get("approved_date"))

                skills = item.get("required_skills") or []
                if isinstance(skills, list):
                    tag_names = [s.get("name", "") if isinstance(s, dict) else str(s) for s in skills]
                else:
                    tag_names = []

                tag_names.append("Campus/Fresher")
                tag_names.append("India")

                listing = StandardJobListing(
                    id=f"unstop-{item.get('id', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "India",
                    is_remote=is_remote,
                    country=country or "India",
                    city=city,
                    employment_type="internship" if opportunity == "internships" else "full_time",
                    posted_at=posted_date,
                    description=f"{title} at {company} via Unstop Campus & Job Network",
                    tags=tag_names,
                    raw_data={
                        "unstop_id": item.get("id"),
                        "views": item.get("viewsCount"),
                        "registered": item.get("registerCount")
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Unstop listing: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} listings from Unstop.")
        return listings

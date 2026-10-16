"""
Archetype A: RemoteOK Engineer & Technical Jobs JSON Adapter (SRC-0050)
Docs / Endpoint: https://remoteok.com/remote-engineer-jobs.json
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("RemoteOKEngineerScraper")


class RemoteOKEngineerScraper(BaseScraper):
    API_URL = "https://remoteok.com/remote-engineer-jobs.json"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0050",
            source_name="RemoteOKEngineer",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching engineer jobs from {self.API_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            res = await self.http_client.get(self.API_URL, headers=headers)
            items = res.json()
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from RemoteOK Engineer: {e}")
            return []

        listings: List[StandardJobListing] = []

        for item in items:
            try:
                # Skip legal notice header
                if not isinstance(item, dict) or "id" not in item:
                    continue

                title = item.get("position", "").strip()
                company = item.get("company", "").strip()
                apply_url = item.get("url", "")
                if not title or not company or not apply_url:
                    continue

                min_sal = item.get("salary_min")
                max_sal = item.get("salary_max")
                salary_min = float(min_sal) if min_sal else None
                salary_max = float(max_sal) if max_sal else None

                location = item.get("location", "").strip() or "Worldwide / Remote"
                tags = item.get("tags", [])
                skills = [t for t in tags if isinstance(t, str)][:8]
                desc = item.get("description", "")[:300]

                listing = StandardJobListing(
                    id=f"remoteok-eng-{item['id']}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=True,
                    employment_type="full_time",
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency="USD" if salary_min else None,
                    description=f"{title} at {company}. {desc}",
                    skills=skills,
                    posted_date=str(item.get("date", ""))[:10] if item.get("date") else None,
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable item: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from RemoteOK Engineer.")
        return listings

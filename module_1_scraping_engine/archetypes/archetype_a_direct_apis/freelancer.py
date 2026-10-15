"""
Archetype A: Freelancer.com Public Projects API Scraper (SRC-0070)
Docs / Endpoint: https://www.freelancer.com/api/projects/0.1/projects/active
"""
from typing import List, Optional
import logging
from datetime import datetime
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("FreelancerScraper")


class FreelancerScraper(BaseScraper):
    API_URL = "https://www.freelancer.com/api/projects/0.1/projects/active"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0070",
            source_name="Freelancer.com",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        params = {"limit": limit or 50, "compact": "false"}
        logger.info(f"[{self.source_id}] Fetching active freelance projects from {self.API_URL}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            data = await self.http_client.get_json(self.API_URL, params=params, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Freelancer: {e}")
            return []

        projects = data.get("result", {}).get("projects", []) if isinstance(data, dict) else []
        if limit:
            projects = projects[:limit]

        listings: List[StandardJobListing] = []
        for p in projects:
            try:
                title = p.get("title", "")
                seo_url = p.get("seo_url", "")
                apply_url = f"https://www.freelancer.com/projects/{seo_url}" if seo_url else f"https://www.freelancer.com/projects/{p.get('id')}"
                if not title:
                    continue

                budget = p.get("budget", {}) or {}
                b_min = budget.get("minimum")
                b_max = budget.get("maximum")
                curr = p.get("currency", {}) or {}
                curr_code = curr.get("code", "USD")

                sal_min, sal_max = None, None
                if b_min is not None and b_max is not None:
                    # Convert to INR estimate using JobNormalizer exchange logic
                    raw_str = f"{curr_code} {b_min} - {b_max}"
                    sal_min, sal_max, _ = JobNormalizer.normalize_salary(raw_str)

                sub_date = p.get("submitdate")
                posted_date = None
                if sub_date:
                    try:
                        posted_date = datetime.utcfromtimestamp(float(sub_date)).isoformat()
                    except Exception:
                        pass

                skills = [j.get("name") for j in p.get("jobs", []) if isinstance(j, dict) and "name" in j]

                listing = StandardJobListing(
                    id=f"freelancer-{p.get('id')}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company="Freelance Client",
                    apply_url=apply_url,
                    location="Remote / Freelance",
                    is_remote=True,
                    employment_type="contract",
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency="INR",
                    posted_at=posted_date,
                    description=p.get("preview_description") or p.get("description"),
                    tags=skills,
                    raw_data={
                        "project_id": p.get("id"),
                        "budget": budget,
                        "currency": curr_code
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing project: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} freelance listings.")
        return listings

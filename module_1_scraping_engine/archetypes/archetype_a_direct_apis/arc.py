"""
Archetype A: Arc.dev Remote Tech Jobs Adapter (SRC-0074)
Docs / Endpoint: https://arc.dev/remote-jobs
"""
from typing import List, Optional
import logging
import json
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("ArcScraper")


class ArcScraper(BaseScraper):
    BASE_URL = "https://arc.dev"
    JOBS_URL = "https://arc.dev/remote-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0074",
            source_name="ArcDev",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching remote tech jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Arc.dev: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script or not script.string:
            logger.error(f"[{self.source_id}] __NEXT_DATA__ script not found in Arc.dev HTML.")
            return []

        try:
            payload = json.loads(script.string)
            page_props = payload.get("props", {}).get("pageProps", {})
            raw_jobs = page_props.get("arcJobs", []) + page_props.get("externalJobs", [])
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to decode Arc.dev JSON payload: {e}")
            return []

        listings: List[StandardJobListing] = []

        for item in raw_jobs:
            try:
                title = item.get("title", "").strip()
                if not title:
                    continue

                url_slug = item.get("urlString", "")
                apply_url = f"{self.BASE_URL}/remote-jobs/{url_slug}" if url_slug else f"{self.JOBS_URL}#{item.get('randomKey', '')}"

                comp_raw = item.get("company", {})
                if isinstance(comp_raw, dict):
                    company = comp_raw.get("name") or comp_raw.get("companyName") or "Remote Tech Company"
                else:
                    company = str(comp_raw) if comp_raw else "Remote Tech Company"

                # Salary
                min_sal = item.get("minAnnualSalary")
                max_sal = item.get("maxAnnualSalary")
                salary_min = float(min_sal) if min_sal else None
                salary_max = float(max_sal) if max_sal else None

                # Categories / Skills
                skills = []
                categories = item.get("categories", [])
                if isinstance(categories, list):
                    for c in categories:
                        if isinstance(c, dict) and "name" in c:
                            skills.append(c["name"])
                        elif isinstance(c, str):
                            skills.append(c)

                # Locations
                req_countries = item.get("requiredCountries", [])
                loc_str = ", ".join(req_countries) if req_countries else "Global / Remote"

                # Experience level
                exp = item.get("experienceLevel") or (item.get("experienceLevels", ["Mid-Senior"])[0] if item.get("experienceLevels") else "Mid-Senior")

                listing = StandardJobListing(
                    id=f"arc-{item.get('randomKey', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc_str,
                    is_remote=True,
                    employment_type=item.get("jobType", "full_time"),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency="USD" if salary_min else None,
                    description=f"{title} at {company}. Experience: {exp}. Skills: {', '.join(skills[:5])}",
                    skills=skills[:8],
                    posted_date=str(item.get("postedAt", ""))[:10] if item.get("postedAt") else None,
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable Arc job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from Arc.dev.")
        return listings

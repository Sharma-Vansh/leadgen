"""
Archetype A: Cutshort India Tech & Startup Jobs Adapter (SRC-0023)
Docs / Endpoint: https://cutshort.io/jobs/software-development-jobs
"""
from typing import List, Optional
import json
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("CutshortScraper")


class CutshortScraper(BaseScraper):
    JOBS_URL = "https://cutshort.io/jobs/software-development-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0023",
            source_name="Cutshort",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching Indian startup jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Cutshort: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        if not next_data_script or not next_data_script.string:
            logger.warning(f"[{self.source_id}] __NEXT_DATA__ not found on Cutshort page.")
            return []

        try:
            data = json.loads(next_data_script.string)
            queries = data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
            raw_jobs = []
            for q in queries:
                q_data = q.get("state", {}).get("data", {}).get("data", {})
                if isinstance(q_data, dict) and "pageData" in q_data:
                    raw_jobs = q_data.get("pageData", {}).get("jobs", [])
                    break
        except Exception as e:
            logger.error(f"[{self.source_id}] Error parsing Cutshort JSON: {e}")
            return []

        if limit:
            raw_jobs = raw_jobs[:limit]

        listings: List[StandardJobListing] = []
        for j in raw_jobs:
            try:
                title = j.get("headline", "")
                company_obj = j.get("companyDetails", {}) or {}
                company = company_obj.get("name", "Tech Startup")
                apply_url = j.get("publicUrl", "")
                if not title or not apply_url:
                    continue

                sal_text = j.get("salaryRangeText")
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(sal_text)

                loc_text = j.get("locationsText") or "India"
                remote_type = j.get("remoteType")
                is_remote_flag = bool(remote_type and "remote" in str(remote_type).lower())
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_text)
                if is_remote_flag:
                    is_remote = True

                skills = j.get("allSkills") or []
                skills = [str(s) for s in skills]

                listing = StandardJobListing(
                    id=f"cutshort-{j.get('_id', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "India",
                    is_remote=is_remote,
                    country=country or "India",
                    city=city,
                    employment_type="full_time",
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency="INR",
                    posted_at=None,
                    description=j.get("sanitizedComment") or f"{title} at {company}",
                    tags=skills + ["Startup", "India"],
                    raw_data={
                        "cutshort_id": j.get("_id"),
                        "exp_range": j.get("expRange"),
                        "remote_type": remote_type
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Cutshort job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

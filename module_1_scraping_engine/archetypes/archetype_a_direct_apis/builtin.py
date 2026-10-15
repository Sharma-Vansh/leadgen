"""
Archetype A: Built In Tech Jobs Adapter (SRC-0049)
Docs / Endpoint: https://builtin.com/jobs/dev-engineering
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("BuiltInScraper")


class BuiltInScraper(BaseScraper):
    BASE_URL = "https://builtin.com"
    JOBS_URL = "https://builtin.com/jobs/dev-engineering"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0049",
            source_name="BuiltIn",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching tech jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from BuiltIn: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", attrs={"data-id": "job-card"})
        listings: List[StandardJobListing] = []

        for card in cards:
            try:
                # 1. Title and link
                job_link_el = card.find("a", href=lambda h: h and h.startswith("/job/"))
                if not job_link_el:
                    continue
                title = job_link_el.text.strip()
                if not title:
                    continue
                apply_url = f"{self.BASE_URL}{job_link_el['href']}"

                # 2. Company
                company = ""
                for comp_a in card.find_all("a", href=lambda h: h and h.startswith("/company/")):
                    t = comp_a.text.strip()
                    if t:
                        company = t
                        break
                if not company:
                    comp_div = card.find("div", class_=lambda x: x and "left-side-tile-item-2" in x)
                    if comp_div and comp_div.text.strip():
                        company = comp_div.text.strip()
                if not company:
                    company = "Tech Company"

                # 3. Location & Workplace Type
                loc_spans = card.find_all("span", class_=lambda x: x and "font-barlow" in x)
                locations = [s.text.strip() for s in loc_spans if s.text.strip()]
                location_str = ", ".join(locations) if locations else "United States / Remote"

                is_remote = any("remote" in s.lower() for s in locations) or "remote" in card.text.lower()

                # 4. Description
                desc_el = card.find("div", class_=lambda x: x and ("fs-sm" in x or "mb-md" in x))
                description = desc_el.text.strip() if desc_el else f"{title} at {company}"

                # 5. Skills
                tags = []
                skills_container = card.find("span", class_=lambda x: x and "d-md-inline" in x)
                if skills_container:
                    tags = [s.text.strip() for s in skills_container.find_all("span") if s.text.strip()]

                listing = StandardJobListing(
                    id=f"builtin-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location_str,
                    is_remote=is_remote,
                    employment_type="full_time",
                    description=description,
                    skills=tags[:8],
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from BuiltIn.")
        return listings

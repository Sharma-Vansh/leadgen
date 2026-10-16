"""
Archetype A: Jobspresso Remote Tech Jobs Adapter (SRC-0043)
Docs / Endpoint: https://jobspresso.co/jm-ajax/get_listings/
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("JobspressoScraper")


class JobspressoScraper(BaseScraper):
    BASE_URL = "https://jobspresso.co"
    AJAX_URL = "https://jobspresso.co/jm-ajax/get_listings/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0043",
            source_name="Jobspresso",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching remote listings from {self.AJAX_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest"
            }
            # Fetch batch of listings via POST
            res = await self.http_client.post(self.AJAX_URL, headers=headers, data={"per_page": limit or 30})
            payload = res.json()
            html_snippet = payload.get("html", "")
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Jobspresso: {e}")
            return []

        soup = BeautifulSoup(html_snippet, "html.parser")
        listings: List[StandardJobListing] = []

        for li in soup.find_all("li"):
            try:
                a_tag = li.find("a", href=True)
                if not a_tag or "/job/" not in a_tag.get("href", ""):
                    continue

                apply_url = a_tag["href"]

                # Extract title from h3 or URL slug
                h3 = li.find("h3") or li.find("div", class_="position")
                if h3 and h3.text.strip():
                    title = h3.text.strip()
                else:
                    slug = apply_url.rstrip("/").split("/")[-1]
                    title = slug.replace("-", " ").title()

                if not title or len(title) < 3:
                    continue

                # Company name
                comp_el = li.find("strong") or li.find("div", class_="company") or li.find("span", class_="company")
                company = comp_el.text.strip() if comp_el and comp_el.text.strip() else "Remote Employer"

                # Location
                loc_el = li.find("div", class_="location") or li.find("span", class_="location")
                location = loc_el.text.strip() if loc_el and loc_el.text.strip() else "Global / Remote"

                # Job type
                type_el = li.find("li", class_="job-type")
                job_type = type_el.text.strip() if type_el else "full_time"

                listing = StandardJobListing(
                    id=f"jobspresso-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=True,
                    employment_type=job_type.lower().replace(" ", "_"),
                    description=f"{title} at {company} ({location}). Full remote opportunity.",
                    skills=["Remote", "Tech"],
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from Jobspresso.")
        return listings

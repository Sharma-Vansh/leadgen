"""
Archetype A: WeAreDevelopers Tech Jobs Adapter (SRC-0057)
Docs / Endpoint: https://www.wearedevelopers.com/en/jobs
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("WeAreDevelopersScraper")


class WeAreDevelopersScraper(BaseScraper):
    BASE_URL = "https://www.wearedevelopers.com"
    JOBS_URL = "https://www.wearedevelopers.com/en/jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0057",
            source_name="WeAreDevelopers",
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
            logger.error(f"[{self.source_id}] Failed to fetch from WeAreDevelopers: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        links = [a for a in soup.find_all("a", href=True) if a["href"].startswith("/jobs/")]
        listings: List[StandardJobListing] = []

        for a in links:
            try:
                href = a.get("href", "")
                apply_url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

                lines = [line.strip() for line in a.text.splitlines() if line.strip()]
                filtered = [
                    l for l in lines
                    if l.lower() not in ["today", "yesterday", "verified", "view details"]
                    and not re.search(r"^\d+\s+(days?|hours?|mins?)\s+ago$", l, re.I)
                    and len(l) > 1
                ]

                if len(filtered) < 2:
                    continue

                title = filtered[0]
                company = filtered[1] if len(filtered) > 1 else "Tech Employer"
                location = filtered[2] if len(filtered) > 2 else "Europe / Remote"

                salary_min = None
                salary_max = None
                salary_currency = "USD"
                skills = []
                is_remote = False

                for item in filtered[2:]:
                    if "remote" in item.lower():
                        is_remote = True
                    sal_match = re.search(r"(\$|€|£)\s*(\d+)k?\s*[–—-]\s*(\$|€|£)?\s*(\d+)k?", item, re.I)
                    if sal_match:
                        sym = sal_match.group(1)
                        salary_currency = "USD" if sym == "$" else ("EUR" if sym == "€" else "GBP")
                        val1 = int(sal_match.group(2))
                        val2 = int(sal_match.group(4))
                        if "k" in item.lower():
                            salary_min = float(val1 * 1000)
                            salary_max = float(val2 * 1000)
                        else:
                            salary_min = float(val1)
                            salary_max = float(val2)
                    elif item.lower() not in ["experienced", "expert", "starter", "mid level", "junior", "senior"]:
                        if len(item) < 30 and not any(c.isdigit() for c in item):
                            skills.append(item)

                listing = StandardJobListing(
                    id=f"wad-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=is_remote or "remote" in location.lower(),
                    employment_type="full_time",
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency=salary_currency if salary_min else "USD",
                    description=f"{title} at {company} in {location}. Skills: {', '.join(skills) if skills else 'Engineering'}",
                    skills=skills[:6],
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from WeAreDevelopers.")
        return listings

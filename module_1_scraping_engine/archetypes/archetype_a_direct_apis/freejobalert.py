"""
Archetype A: FreeJobAlert Government, Bank & IT Jobs Adapter (SRC-0258)
Docs / Endpoint: https://www.freejobalert.com/latest-notifications/
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("FreeJobAlertScraper")


class FreeJobAlertScraper(BaseScraper):
    BASE_URL = "https://www.freejobalert.com"
    NOTIFICATIONS_URL = "https://www.freejobalert.com/latest-notifications/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0258",
            source_name="FreeJobAlert",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching latest job notifications from {self.NOTIFICATIONS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.NOTIFICATIONS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from FreeJobAlert: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr")
        listings: List[StandardJobListing] = []
        seen_urls = set()

        for row in rows:
            try:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue

                # Col 0: Date, Col 1: Recruitment Board/Company, Col 2: Post Name & vacancies, Col 3: Qualification
                date_str = cols[0].text.strip()
                company = cols[1].text.strip()
                title_col = cols[2].text.strip()

                if not company or not title_col or "Post Date" in date_str or "Recruitment Board" in company:
                    continue

                # Clean Title
                title = re.sub(r"\s+", " ", title_col)
                # Find link
                link_el = row.find("a", href=True)
                if not link_el:
                    continue

                apply_url = link_el["href"]
                if apply_url in seen_urls:
                    continue
                seen_urls.add(apply_url)

                qualification = cols[3].text.strip() if len(cols) > 3 else "Graduate"

                listing = StandardJobListing(
                    id=f"fja-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=f"{title} - {company}",
                    company=company,
                    apply_url=apply_url,
                    location="India",
                    is_remote=False,
                    employment_type="full_time",
                    description=f"{title} recruitment by {company}. Qualification: {qualification}. Notification date: {date_str}.",
                    skills=[qualification, "Government / Public Sector"],
                    posted_date=date_str if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str) else None,
                    raw_payload={"raw_title": title, "raw_company": company, "qualification": qualification}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable row: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} notifications from FreeJobAlert.")
        return listings

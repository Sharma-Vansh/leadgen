"""
Archetype A: Web3 & Blockchain Tech Jobs Adapter (SRC-0071)
Docs / Endpoint: https://web3.career/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("Web3CareerScraper")


class Web3CareerScraper(BaseScraper):
    BASE_URL = "https://web3.career"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0071",
            source_name="Web3Career",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching Web3 tech jobs from {self.BASE_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.BASE_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Web3Career: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr", class_=lambda x: x and "table_row" in x)
        listings: List[StandardJobListing] = []

        for row in rows:
            try:
                h2 = row.find("h2")
                title = h2.text.strip() if h2 else ""
                if not title:
                    continue

                comp_el = row.find("h3") or row.find("a", class_=lambda x: x and "company" in str(x))
                company = comp_el.text.strip() if comp_el else "Web3 Startup"

                # Find job link
                links = row.find_all("a", href=True)
                apply_url = ""
                for l in links:
                    href = l["href"]
                    if "-job" in href or href.count("/") >= 2:
                        apply_url = f"{self.BASE_URL}{href}" if href.startswith("/") else href
                        break

                if not apply_url:
                    continue

                listing = StandardJobListing(
                    id=f"web3-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location="Remote / Global",
                    is_remote=True,
                    employment_type="full_time",
                    posted_at=None,
                    description=f"{title} at {company} in Web3 ecosystem",
                    tags=["Web3", "Blockchain", "Remote"],
                    raw_data={
                        "raw_title": title
                    }
                )
                listings.append(listing)
                if limit and len(listings) >= limit:
                    break
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Web3Career job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

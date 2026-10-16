"""
Archetype A: CryptocurrencyJobs Live RSS Feed Adapter (SRC-0073)
Docs / Endpoint: https://cryptocurrencyjobs.co/index.xml
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("CryptoCurrencyJobsScraper")


class CryptoCurrencyJobsScraper(BaseScraper):
    RSS_URL = "https://cryptocurrencyjobs.co/index.xml"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0073",
            source_name="CryptoCurrencyJobs",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching cryptocurrency tech jobs from {self.RSS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.RSS_URL, headers=headers)
            xml_text = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from CryptocurrencyJobs: {e}")
            return []

        soup = BeautifulSoup(xml_text, "xml")
        items = soup.find_all("item")
        listings: List[StandardJobListing] = []

        for item in items:
            try:
                title_el = item.find("title")
                raw_title = title_el.text.strip() if title_el else ""
                if not raw_title or len(raw_title) < 3:
                    continue

                link_el = item.find("link")
                apply_url = link_el.text.strip() if link_el else ""
                if not apply_url:
                    continue

                # Format usually: "Role at Company"
                title = raw_title
                company = "Crypto Startup"
                if " at " in raw_title:
                    title_part, comp_part = raw_title.rsplit(" at ", 1)
                    title = title_part.strip()
                    company = comp_part.strip()

                desc_el = item.find("description")
                desc = desc_el.text.strip() if desc_el else f"{title} at {company} in the Web3/Crypto space."

                pub_date_el = item.find("pubDate")
                pub_date = str(pub_date_el.text)[:10] if pub_date_el and pub_date_el.text else None

                listing = StandardJobListing(
                    id=f"ccj-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location="Global / Remote",
                    is_remote=True,
                    employment_type="full_time",
                    description=desc[:300],
                    skills=["Web3", "Blockchain", "Crypto"],
                    posted_date=pub_date,
                    raw_payload={"raw_title": raw_title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable item: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from CryptoCurrencyJobs.")
        return listings

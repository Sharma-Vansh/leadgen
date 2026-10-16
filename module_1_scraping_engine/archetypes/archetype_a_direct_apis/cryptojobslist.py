"""
Archetype A: CryptoJobsList Tech & Blockchain Jobs Adapter (SRC-0072)
Docs / Endpoint: https://cryptojobslist.com/rss.xml
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("CryptoJobsListScraper")


class CryptoJobsListScraper(BaseScraper):
    RSS_URL = "https://cryptojobslist.com/rss.xml"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0072",
            source_name="CryptoJobsList",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching blockchain tech jobs from {self.RSS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.RSS_URL, headers=headers)
            xml_text = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from CryptoJobsList: {e}")
            return []

        soup = BeautifulSoup(xml_text, "xml")
        items = soup.find_all("item")
        listings: List[StandardJobListing] = []

        for item in items:
            try:
                title_el = item.find("title")
                title = title_el.text.strip() if title_el else ""
                if not title or len(title) < 3 or "Apply Here" in title:
                    continue

                link_el = item.find("link")
                apply_url = link_el.text.strip() if link_el else ""
                if not apply_url:
                    continue

                # Parse company and location from URL structure: ...-at-{company}
                company = "Crypto Startup"
                location = "Global / Remote"
                if "-at-" in apply_url:
                    comp_part = apply_url.split("-at-")[-1].replace("/", "")
                    company = comp_part.replace("-", " ").title()

                desc_el = item.find("description")
                desc = desc_el.text.strip() if desc_el else f"{title} at {company}."

                pub_date_el = item.find("pubDate")
                pub_date = str(pub_date_el.text)[:10] if pub_date_el and pub_date_el.text else None

                listing = StandardJobListing(
                    id=f"cjl-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=True,
                    employment_type="full_time",
                    description=f"{title} at {company}. Web3/crypto ecosystem role.",
                    skills=["Web3", "Blockchain", "Smart Contracts", "Crypto"],
                    posted_date=pub_date,
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable RSS item: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from CryptoJobsList.")
        return listings

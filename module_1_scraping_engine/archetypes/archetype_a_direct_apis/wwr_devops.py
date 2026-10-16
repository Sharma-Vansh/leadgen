"""
Archetype A: WeWorkRemotely DevOps & Sysadmin Feed Adapter (SRC-0041)
Docs / Endpoint: https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("WWRDevOpsScraper")


class WWRDevOpsScraper(BaseScraper):
    RSS_URL = "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0041",
            source_name="WWRDevOps",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching DevOps jobs from {self.RSS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.RSS_URL, headers=headers)
            xml_text = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from WWR DevOps RSS: {e}")
            return []

        soup = BeautifulSoup(xml_text, "xml")
        items = soup.find_all("item")
        listings: List[StandardJobListing] = []

        for item in items:
            try:
                title_el = item.find("title")
                raw_title = title_el.text.strip() if title_el else ""
                if not raw_title:
                    continue

                link_el = item.find("link")
                apply_url = link_el.text.strip() if link_el else ""
                if not apply_url:
                    continue

                company = "Remote Tech Company"
                title = raw_title
                if ":" in raw_title:
                    parts = raw_title.split(":", 1)
                    company = parts[0].strip()
                    title = parts[1].strip()

                desc_el = item.find("description")
                desc = desc_el.text.strip() if desc_el else f"{title} at {company}."

                pub_date_el = item.find("pubDate")
                pub_date = str(pub_date_el.text)[:10] if pub_date_el and pub_date_el.text else None

                listing = StandardJobListing(
                    id=f"wwr-devops-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location="Global / Remote",
                    is_remote=True,
                    employment_type="full_time",
                    description=desc[:300],
                    skills=["DevOps", "SysAdmin", "Cloud", "Infrastructure", "Kubernetes"],
                    posted_date=pub_date,
                    raw_payload={"raw_title": raw_title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable item: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from WWR DevOps.")
        return listings

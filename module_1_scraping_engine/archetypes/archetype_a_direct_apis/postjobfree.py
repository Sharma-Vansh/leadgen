"""
Archetype A: PostJobFree Tech Jobs Aggregator Adapter (SRC-0010)
Docs / Endpoint: https://www.postjobfree.com/jobs?q=developer
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("PostJobFreeScraper")


class PostJobFreeScraper(BaseScraper):
    BASE_URL = "https://www.postjobfree.com"
    SEARCH_URL = "https://www.postjobfree.com/jobs?q=developer"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0010",
            source_name="PostJobFree",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching tech jobs from {self.SEARCH_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.SEARCH_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from PostJobFree: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        listings: List[StandardJobListing] = []
        seen_urls = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("/job/") or href in seen_urls:
                continue
            seen_urls.add(href)

            try:
                title = a.text.strip()
                if not title or len(title) < 4:
                    continue

                apply_url = f"{self.BASE_URL}{href}"
                card = a.find_parent("div") or a.find_parent("td")
                card_text = card.get_text(separator=" | ", strip=True) if card else ""
                parts = [p.strip() for p in card_text.split(" | ") if p.strip()]

                company = "Hiring Employer"
                if len(parts) > 1 and parts[1] != "?":
                    company = parts[1]

                location = "United States"
                if len(parts) > 3 and not "USD" in parts[3]:
                    location = parts[3]

                # Salary regex: 70000USD - 110000USD per year
                salary_min = None
                salary_max = None
                salary_currency = "USD"
                sal_match = re.search(r"(\d+)\s*(?:USD|\$)?\s*-\s*(\d+)\s*USD", card_text)
                if sal_match:
                    salary_min = float(sal_match.group(1))
                    salary_max = float(sal_match.group(2))

                is_remote = "remote" in card_text.lower()

                listing = StandardJobListing(
                    id=f"pjf-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=is_remote,
                    employment_type="full_time",
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency=salary_currency if salary_min else None,
                    description=f"{title} at {company} ({location}). {card_text[:250]}",
                    skills=["Software Engineering", "Developer"],
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable item: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from PostJobFree.")
        return listings

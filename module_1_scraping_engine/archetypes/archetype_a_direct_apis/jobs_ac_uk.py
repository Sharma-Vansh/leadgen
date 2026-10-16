"""
Archetype A: Jobs.ac.uk Tech & Research Jobs Adapter (SRC-0058)
Docs / Endpoint: https://www.jobs.ac.uk/search/?keywords=software
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("JobsAcUkScraper")


class JobsAcUkScraper(BaseScraper):
    BASE_URL = "https://www.jobs.ac.uk"
    SEARCH_URL = "https://www.jobs.ac.uk/search/?keywords=software"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0058",
            source_name="JobsAcUk",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching software and tech jobs from {self.SEARCH_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.SEARCH_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Jobs.ac.uk: {e}")
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
                card = a.find_parent("div", class_=lambda x: x and ("job" in str(x) or "result" in str(x) or "card" in str(x)))
                card_text = card.get_text(separator=" | ", strip=True) if card else ""

                # Extract Employer / University
                parts = [p.strip() for p in card_text.split(" | ") if p.strip()]
                company = "UK University / Institute"
                if len(parts) > 2:
                    for part in parts[1:4]:
                        if any(term in part.lower() for term in ["university", "college", "institute", "school", "department", "council", "trust", "ltd"]):
                            company = part
                            break

                # Extract Salary
                salary_min = None
                salary_max = None
                sal_match = re.search(r"£\s*([\d,]+)\s*(?:to|-)\s*£?\s*([\d,]+)", card_text)
                if sal_match:
                    salary_min = float(sal_match.group(1).replace(",", ""))
                    salary_max = float(sal_match.group(2).replace(",", ""))

                # Extract Location
                location = "United Kingdom"
                if "Location:" in card_text:
                    loc_part = card_text.split("Location:")[1].split("|")[0].strip()
                    if loc_part:
                        location = loc_part

                is_remote = "remote" in card_text.lower() or "hybrid" in card_text.lower()

                listing = StandardJobListing(
                    id=f"jobsacuk-{hash(apply_url)}",
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
                    salary_currency="GBP" if salary_min else None,
                    description=f"{title} at {company}. Location: {location}. Details: {card_text[:250]}",
                    skills=["Academic", "Software Engineering", "Research"],
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from Jobs.ac.uk.")
        return listings

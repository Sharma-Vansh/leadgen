"""
Archetype A: DailyRemote Software Development Jobs Adapter (SRC-0054)
Docs / Endpoint: https://dailyremote.com/remote-software-development-jobs
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("DailyRemoteScraper")


class DailyRemoteScraper(BaseScraper):
    BASE_URL = "https://dailyremote.com"
    JOBS_URL = "https://dailyremote.com/remote-software-development-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0054",
            source_name="DailyRemote",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching remote dev jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from DailyRemote: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("article")
        listings: List[StandardJobListing] = []

        for art in articles:
            try:
                a_tag = art.find("a", href=True)
                if not a_tag or "/remote-job/" not in a_tag.get("href", ""):
                    continue

                href = a_tag["href"]
                apply_url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

                h2 = art.find(["h2", "h3"])
                title = h2.text.strip() if h2 else ""
                if not title or len(title) < 3:
                    continue

                card_text = art.get_text(separator=" | ", strip=True)
                parts = [p.strip() for p in card_text.split(" | ") if p.strip()]

                company = "Remote Tech Company"
                if len(parts) > 1 and parts[1] != "?":
                    company = parts[1]

                # Location
                location = "Worldwide / Remote"
                for p in parts:
                    if p.lower() in ["worldwide", "united states", "europe", "uk", "canada", "remote"]:
                        location = p
                        break

                # Salary regex: $75100 - $103K per year
                salary_min = None
                salary_max = None
                salary_currency = "USD"
                sal_match = re.search(r"\$\s*([\d,]+)\s*(?:-|to)\s*\$?([\d,]+)(k)?\s*per year", card_text, re.I)
                if sal_match:
                    v1 = float(sal_match.group(1).replace(",", ""))
                    v2 = float(sal_match.group(2).replace(",", ""))
                    if sal_match.group(3):
                        v2 *= 1000
                    salary_min = v1
                    salary_max = v2

                # Skills
                skills = []
                for s in ["Python", "JavaScript", "React", "Node", "AWS", "Go", "Rust", "Java", "Cloud", "Blockchain"]:
                    if s.lower() in card_text.lower():
                        skills.append(s)

                listing = StandardJobListing(
                    id=f"dailyremote-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=True,
                    employment_type="full_time",
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency=salary_currency if salary_min else None,
                    description=f"{title} at {company}. {card_text[:250]}",
                    skills=skills,
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable article: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from DailyRemote.")
        return listings

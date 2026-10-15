"""
Archetype E: LinkedIn Zero-Login Guest API Scraper (SRC-0002)
Bypasses LinkedIn login authwall by utilizing the public guest search endpoint:
https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
"""
from typing import List, Optional
import logging
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.core.human_behavior import HumanBehavior

logger = logging.getLogger("LinkedInGuestScraper")


class LinkedInGuestScraper(BaseScraper):
    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0002",
            source_name="LinkedIn Jobs (Guest Mode)",
            archetype="E",
            http_client=http_client
        )

    async def scrape(
        self,
        limit: Optional[int] = 10,
        keyword: str = "Software Engineer",
        location: str = "India"
    ) -> List[StandardJobListing]:
        url = f"{self.BASE_URL}?keywords={quote_plus(keyword)}&location={quote_plus(location)}&start=0"
        logger.info(f"[{self.source_id}] Querying LinkedIn Guest endpoint for '{keyword}' in '{location}'...")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate"
        }

        try:
            resp = await self.http_client.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from LinkedIn: {e}")
            return []

        cards = soup.select("li, .base-card, .job-search-card")
        if limit:
            cards = cards[:limit]

        listings: List[StandardJobListing] = []
        for idx, card in enumerate(cards):
            try:
                title_elem = card.select_one(".base-search-card__title, h3")
                comp_elem = card.select_one(".base-search-card__subtitle, h4, .job-search-card__company-name")
                loc_elem = card.select_one(".job-search-card__location")
                link_elem = card.select_one("a.base-card__full-link, a")

                title = title_elem.get_text(strip=True) if title_elem else None
                company = comp_elem.get_text(strip=True) if comp_elem else None
                apply_url = link_elem.get("href") if link_elem else None

                if not title or not company or not apply_url:
                    continue

                if "?" in apply_url:
                    apply_url = apply_url.split("?")[0]  # Strip tracking params

                loc_raw = loc_elem.get_text(strip=True) if loc_elem else "India"
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                listing = StandardJobListing(
                    id=f"linkedin-{idx}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country or "India",
                    city=city,
                    employment_type="full_time",
                    skills=[keyword],
                    raw_payload={"keyword": keyword, "location": location}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing card: {ex}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} listings from LinkedIn.")
        return listings

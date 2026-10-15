"""
Archetype A: PeoplePerHour Freelance & Tech Projects Adapter (SRC-0076)
Docs / Endpoint: https://www.peopleperhour.com/freelance-jobs/technology-programming
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("PeoplePerHourScraper")


class PeoplePerHourScraper(BaseScraper):
    BASE_URL = "https://www.peopleperhour.com"
    PROJECTS_URL = "https://www.peopleperhour.com/freelance-jobs/technology-programming"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0076",
            source_name="PeoplePerHour",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching freelance projects from {self.PROJECTS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.PROJECTS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from PeoplePerHour: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", class_=lambda x: x and ("item--container" in str(x) or "project-item" in str(x)))
        if not cards:
            cards = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/freelance-jobs/" in href and re.search(r"-\d{5,}", href):
                    container = a.find_parent("div", class_=lambda x: x and ("card" in str(x) or "item" in str(x) or "row" in str(x)))
                    if container and container not in cards:
                        cards.append(container)

        listings: List[StandardJobListing] = []

        for card in cards:
            try:
                # 1. Title and link
                proj_link = None
                for a in card.find_all("a", href=True):
                    href = a["href"]
                    if "/freelance-jobs/" in href and re.search(r"-\d{5,}", href):
                        proj_link = a
                        break

                if not proj_link:
                    continue

                title = proj_link.text.strip()
                if not title or len(title) < 5:
                    continue

                href = proj_link["href"]
                apply_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                # 2. Client / Company
                client_el = card.find("a", href=lambda h: h and "/freelancer/" in h)
                client_name = client_el.text.strip().replace("by", "").strip() if client_el else "Verified Client"

                # 3. Budget / Salary
                card_text = card.get_text(separator=" ", strip=True)
                salary_min = None
                salary_currency = "USD"
                price_match = re.search(r"(\$|£|€)\s*([\d,]+)", card_text)
                if price_match:
                    sym = price_match.group(1)
                    salary_currency = "USD" if sym == "$" else ("GBP" if sym == "£" else "EUR")
                    salary_min = float(price_match.group(2).replace(",", ""))

                # 4. Description
                desc_el = card.find("p")
                description = desc_el.text.strip() if desc_el else f"Freelance project: {title} posted by {client_name}"

                listing = StandardJobListing(
                    id=f"pph-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=f"Client ({client_name})",
                    apply_url=apply_url,
                    location="Remote Freelance",
                    is_remote=True,
                    employment_type="contract",
                    salary_min=salary_min,
                    salary_currency=salary_currency,
                    description=description,
                    skills=["Freelance", "Contract", "Tech Development"],
                    raw_payload={"raw_title": title, "raw_client": client_name}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} projects from PeoplePerHour.")
        return listings

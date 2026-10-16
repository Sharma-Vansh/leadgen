"""
Archetype A: OneForma AI & Remote Projects Adapter (SRC-0089)
Docs / Endpoint: https://jobs.oneforma.com/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("OneFormaScraper")


class OneFormaScraper(BaseScraper):
    BASE_URL = "https://www.oneforma.com"
    PROJECTS_URL = "https://jobs.oneforma.com/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0089",
            source_name="OneForma",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching AI and data projects from {self.PROJECTS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.PROJECTS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from OneForma: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("article") or soup.find_all("div", class_=lambda x: x and ("project" in x or "job" in x))
        listings: List[StandardJobListing] = []
        seen_urls = set()

        for art in articles:
            try:
                # Find project link
                proj_link = None
                for a in art.find_all("a", href=True):
                    href = a["href"]
                    if "/projects/" in href and href != "https://www.oneforma.com/projects/":
                        proj_link = a
                        break

                if not proj_link:
                    continue

                apply_url = proj_link["href"]
                if apply_url in seen_urls:
                    continue
                seen_urls.add(apply_url)

                # Title
                h2 = art.find(["h2", "h3", "h4"])
                title = h2.text.strip() if h2 else proj_link.text.strip()
                if not title or len(title) < 4:
                    slug = apply_url.rstrip("/").split("/")[-1]
                    title = slug.replace("-", " ").title()

                card_text = art.get_text(separator=" | ", strip=True)
                desc = card_text[:300]

                listing = StandardJobListing(
                    id=f"oneforma-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company="OneForma Centific",
                    apply_url=apply_url,
                    location="Global / Remote",
                    is_remote=True,
                    employment_type="contract",
                    description=f"{title} - AI and machine learning gig project. {desc}",
                    skills=["AI Training", "Data Annotation", "Freelance", "LLM Evaluation"],
                    raw_payload={"raw_title": title, "raw_card": card_text[:200]}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable article: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} projects from OneForma.")
        return listings

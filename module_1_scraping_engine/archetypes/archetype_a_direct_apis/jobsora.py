"""
Archetype A: Jobsora Global / India Aggregator Adapter (SRC-0013)
Docs / Endpoint: https://in.jobsora.com/jobs-developer
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("JobsoraScraper")


class JobsoraScraper(BaseScraper):
    JOBS_URL = "https://in.jobsora.com/jobs-developer"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0013",
            source_name="Jobsora",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching developer jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Jobsora: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("article")
        if limit:
            articles = articles[:limit]

        listings: List[StandardJobListing] = []
        for art in articles:
            try:
                title_a = art.find("a", href=True)
                if not title_a:
                    continue

                title = title_a.text.strip()
                apply_url = title_a["href"]
                if not title or not apply_url:
                    continue

                if apply_url.startswith("/"):
                    apply_url = f"https://in.jobsora.com{apply_url}"

                # Text blocks usually contain: Title, Company, Location, Description
                text_parts = [p.strip() for p in art.text.split("\n") if p.strip()]
                company = text_parts[1] if len(text_parts) > 1 else "Employer"
                loc_raw = text_parts[2] if len(text_parts) > 2 else "India"

                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                desc = " ".join(text_parts[3:]) if len(text_parts) > 3 else f"{title} at {company}"

                listing = StandardJobListing(
                    id=f"jobsora-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "India",
                    is_remote=is_remote,
                    country=country or "India",
                    city=city,
                    employment_type="full_time",
                    posted_at=None,
                    description=desc[:500],
                    tags=["Developer", "India"],
                    raw_data={
                        "raw_location": loc_raw
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Jobsora listing: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

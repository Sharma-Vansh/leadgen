"""
Archetype A: Placement India Jobs Adapter (SRC-0018)
Docs / Endpoint: https://www.placementindia.com/job-search/software-developer-jobs.htm
"""
from typing import List, Optional
import re
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("PlacementIndiaScraper")


class PlacementIndiaScraper(BaseScraper):
    JOBS_URL = "https://www.placementindia.com/job-search/software-developer-jobs.htm"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0018",
            source_name="PlacementIndia",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching Indian developer jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from PlacementIndia: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        job_links = [a for a in links if "/job-detail/" in a["href"]]

        # Deduplicate while preserving order
        seen_urls = set()
        unique_links = []
        for a in job_links:
            url = a["href"]
            if url not in seen_urls and a.text.strip():
                seen_urls.add(url)
                unique_links.append(a)

        if limit:
            unique_links = unique_links[:limit]

        listings: List[StandardJobListing] = []
        for a in unique_links:
            try:
                title = a.text.strip()
                apply_url = a["href"]
                if not title or not apply_url:
                    continue

                # Parse company and city from URL: /job-detail/{role}-in-{company}-at-{city}-{id}.htm
                company = "Indian Employer"
                city = "India"
                match = re.search(r"-in-(.*?)-at-(.*?)-(\d+)\.htm", apply_url)
                job_id = None
                if match:
                    comp_slug, city_slug, job_id = match.groups()
                    company = comp_slug.replace("-", " ").title()
                    city = city_slug.replace("-", " ").title()
                else:
                    id_match = re.search(r"-(\d+)\.htm", apply_url)
                    if id_match:
                        job_id = id_match.group(1)

                loc, is_remote, country, c_city = JobNormalizer.normalize_location(city)

                listing = StandardJobListing(
                    id=f"pi-{job_id or hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=city,
                    is_remote=is_remote,
                    country="India",
                    city=c_city or city,
                    employment_type="full_time",
                    posted_at=None,
                    description=f"{title} at {company} located in {city}, India",
                    tags=["India", "Developer", "IT"],
                    raw_data={
                        "placement_india_id": job_id
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing PlacementIndia listing: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

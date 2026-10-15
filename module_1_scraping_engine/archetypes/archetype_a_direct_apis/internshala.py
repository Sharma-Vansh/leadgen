"""
Archetype A: Internshala Freshers & Jobs Adapter (SRC-0026)
Docs / Endpoint: https://internshala.com/jobs/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("InternshalaScraper")


class InternshalaScraper(BaseScraper):
    BASE_URL = "https://internshala.com"
    JOBS_URL = "https://internshala.com/jobs/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0026",
            source_name="Internshala",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching fresher jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Internshala: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", class_=lambda x: x and "individual_internship" in x)
        listings: List[StandardJobListing] = []

        for card in cards:
            try:
                title_el = card.find("a", class_="job-title-href")
                comp_el = card.find(class_="company-name")
                
                title = title_el.text.strip() if title_el else ""
                href = title_el["href"] if title_el and "href" in title_el.attrs else ""
                if not href:
                    href = card.get("data-href", "")

                company = comp_el.text.strip() if comp_el else ""

                if not title or not href:
                    continue

                apply_url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

                loc_el = card.find(id="location_names") or card.find(class_="location_link")
                loc_raw = loc_el.text.strip() if loc_el else "India"
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                # Salary or CTC
                sal_el = card.find(class_="desktop-text")
                sal_raw = sal_el.text.strip() if sal_el else None
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(sal_raw)

                job_id = card.get("internshipid") or hash(apply_url)

                listing = StandardJobListing(
                    id=f"internshala-{job_id}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company or "Hiring Company",
                    apply_url=apply_url,
                    location=loc or "India",
                    is_remote=is_remote,
                    country=country or "India",
                    city=city,
                    employment_type="full_time",
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency="INR",
                    posted_at=None,
                    description=f"{title} at {company} in {loc_raw}",
                    tags=["Fresher", "Entry Level", "India"],
                    raw_data={
                        "internship_id": card.get("internshipid"),
                        "raw_location": loc_raw
                    }
                )
                listings.append(listing)
                if limit and len(listings) >= limit:
                    break
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Internshala job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings

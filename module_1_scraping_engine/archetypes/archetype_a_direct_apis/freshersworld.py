"""
Archetype A: Freshersworld India Jobs Adapter (SRC-0007)
Docs / Endpoint: https://www.freshersworld.com/jobs/jobsearch/software-developer-jobs
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("FreshersworldScraper")


class FreshersworldScraper(BaseScraper):
    BASE_URL = "https://www.freshersworld.com"
    JOBS_URL = "https://www.freshersworld.com/jobs/jobsearch/software-developer-jobs"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0007",
            source_name="Freshersworld",
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
            logger.error(f"[{self.source_id}] Failed to fetch from Freshersworld: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        seen_urls = set()
        listings: List[StandardJobListing] = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not re.search(r"-\d{5,}", href) or "/jobs/" not in href:
                continue
            if href in seen_urls:
                continue
            seen_urls.add(href)

            try:
                card = a.find_parent("div", class_=lambda x: x and ("job" in str(x) or "wrap" in str(x) or "card" in str(x) or "block" in str(x)))
                if not card:
                    continue

                card_text = card.get_text(separator=" | ", strip=True)

                slug = href.split("/")[-1]
                slug_clean = re.sub(r"-\d+$", "", slug)
                title_match = re.split(r"-jobs?-opening-in-", slug_clean, flags=re.I)
                if title_match:
                    title = title_match[0].replace("-", " ").title()
                else:
                    title = "Software Engineer"

                apply_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                company = "Tech Employer"
                if len(title_match) > 1:
                    comp_part = title_match[1].split("-at-")[0]
                    company = comp_part.replace("-", " ").title()

                location = "India"
                if "-at-" in slug_clean:
                    loc_part = slug_clean.split("-at-")[-1]
                    location = loc_part.replace("-", " ").title() + ", India"

                salary_min = None
                salary_max = None
                sal_match = re.search(r"(\d{4,6})\s*-\s*(\d{4,6})\s*Monthly", card_text, re.I)
                if sal_match:
                    salary_min = float(sal_match.group(1)) * 12
                    salary_max = float(sal_match.group(2)) * 12

                skills = []
                for s in ["Python", "Java", "React", "Node", "SQL", "BE/B.Tech", "BCA", "BSc", "Full Stack", "Data Science"]:
                    if s.lower() in card_text.lower():
                        skills.append(s)

                listing = StandardJobListing(
                    id=f"fw-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=False,
                    employment_type="full_time",
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency="INR" if salary_min else None,
                    description=f"{title} opening at {company} in {location}. Details: {card_text[:250]}",
                    skills=skills,
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} fresher jobs from Freshersworld.")
        return listings

"""
Archetype A: Remote Rocketship Tech Jobs Adapter (SRC-0044)
Docs / Endpoint: https://www.remoterocketship.com/jobs/python-developer/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("RemoteRocketshipScraper")


class RemoteRocketshipScraper(BaseScraper):
    BASE_URL = "https://www.remoterocketship.com"
    JOBS_URL = "https://www.remoterocketship.com/jobs/python-developer/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0044",
            source_name="RemoteRocketship",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching remote jobs from {self.JOBS_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.JOBS_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Remote Rocketship: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", class_=lambda x: x and ("rounded-lg" in x or "border-subtle" in x))
        listings: List[StandardJobListing] = []

        for card in cards:
            try:
                # 1. Job Title from H3
                h3 = card.find("h3")
                if not h3:
                    continue
                title = h3.get_text(strip=True)
                if not title or len(title) < 3 or title.endswith("Jobs"):
                    continue

                # Link
                job_link = h3.find("a", href=True) or card.find("a", href=lambda h: h and "/jobs/" in h and not h.endswith("/jobs/"))
                if not job_link:
                    continue
                href = job_link["href"]
                apply_url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

                # 2. Company Name
                company = "Remote Tech Company"
                for comp_a in card.find_all("a", href=lambda h: h and "/company/" in h):
                    t = comp_a.get_text(strip=True)
                    if t and t not in ["All Job Openings", "Website", "LinkedIn", "Apply", "View Job", title]:
                        company = t
                        break

                # 3. Description
                desc_el = card.find("p") or card.find("div", class_=lambda x: x and "text-subtle" in str(x))
                desc_text = desc_el.text.strip() if desc_el else f"{title} at {company}"

                # 4. Location
                card_text = card.get_text(separator=" ", strip=True)
                location_str = "Global / Remote"
                for part in card_text.split("•"):
                    if "remote" in part.lower():
                        location_str = part.strip()
                        break

                # 5. Tags / Skills
                tag_links = card.find_all("a", href=lambda h: h and "/jobs/" in h and not "/company/" in h)
                tags = [t.text.strip() for t in tag_links if t.text.strip() and t.text.strip() not in [title, "All Job Openings"]][:8]

                listing = StandardJobListing(
                    id=f"rr-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location_str,
                    is_remote=True,
                    employment_type="full_time",
                    description=desc_text,
                    skills=tags,
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from Remote Rocketship.")
        return listings

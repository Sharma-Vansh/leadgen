"""
Archetype A: HackerNews Who is Hiring Official API Adapter (SRC-0046)
Docs / Endpoint: https://hacker-news.firebaseio.com/v0/user/whoishiring.json
"""
from typing import List, Optional
import logging
import re
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("HNWhoIsHiringScraper")


class HNWhoIsHiringScraper(BaseScraper):
    USER_API = "https://hacker-news.firebaseio.com/v0/user/whoishiring.json"
    ITEM_API = "https://hacker-news.firebaseio.com/v0/item/{}.json"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0046",
            source_name="HNWhoIsHiring",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching latest Who is Hiring threads from Firebase...")

        try:
            res = await self.http_client.get(self.USER_API)
            user_data = res.json()
            submitted = user_data.get("submitted", [])
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch user submissions: {e}")
            return []

        # Find latest 'Who is hiring' thread
        thread_id = None
        for item_id in submitted[:10]:
            try:
                res_item = await self.http_client.get(self.ITEM_API.format(item_id))
                item_data = res_item.json()
                if item_data and "who is hiring" in item_data.get("title", "").lower():
                    thread_id = item_id
                    job_comment_ids = item_data.get("kids", [])
                    break
            except Exception:
                continue

        if not thread_id or not job_comment_ids:
            logger.warning(f"[{self.source_id}] No active Who is Hiring thread found.")
            return []

        listings: List[StandardJobListing] = []
        target_count = limit or 30

        for kid_id in job_comment_ids[:target_count * 2]:
            try:
                r_c = await self.http_client.get(self.ITEM_API.format(kid_id))
                comment = r_c.json()
                if not comment or comment.get("deleted") or comment.get("dead"):
                    continue

                raw_html = comment.get("text", "")
                if not raw_html or len(raw_html) < 20:
                    continue

                soup = BeautifulSoup(raw_html, "html.parser")
                clean_text = soup.get_text(separator=" | ", strip=True)
                lines = [line.strip() for line in clean_text.split(" | ") if line.strip()]
                if not lines:
                    continue

                # Top line format is usually: Company | Role | Location | Remote/Onsite
                header_line = lines[0]
                header_parts = [p.strip() for p in header_line.split("|")]
                company = header_parts[0] if len(header_parts) > 0 else "HN Startup"
                title = header_parts[1] if len(header_parts) > 1 else "Software Engineer"
                location = header_parts[2] if len(header_parts) > 2 else "Remote"

                is_remote = "remote" in clean_text.lower()
                apply_url = f"https://news.ycombinator.com/item?id={kid_id}"

                listing = StandardJobListing(
                    id=f"hn-wih-{kid_id}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=location,
                    is_remote=is_remote,
                    employment_type="full_time",
                    description=f"{title} at {company}. {clean_text[:300]}",
                    skills=["Tech", "Startup", "Engineering"],
                    raw_payload={"raw_title": title, "raw_company": company, "hn_id": kid_id}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping comment {kid_id}: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from HN Who is Hiring.")
        return listings

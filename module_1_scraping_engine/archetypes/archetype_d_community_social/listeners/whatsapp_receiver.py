"""
Archetype D, Tier 1: WhatsApp Opt-in Broadcast & Forwarding Bot Receiver (SRC-0382)
Handles inbound webhook payloads from Meta Cloud API when placement coordinators
or students forward hiring alerts to the LeadGen business number.
"""
from typing import List, Optional, Dict, Any
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.spam_filter import SpamFilter
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.entity_extractor import EntityExtractor
from module_1_scraping_engine.archetypes.archetype_d_community_social.parsers.link_unshortener import LinkUnshortener

logger = logging.getLogger("WhatsAppReceiver")


class WhatsAppReceiver(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0382",
            source_name="WhatsApp Forwarding Bot",
            archetype="D",
            http_client=http_client
        )
        self.spam_filter = SpamFilter()
        self.entity_extractor = EntityExtractor()
        self.link_unshortener = LinkUnshortener()

    async def process_webhook_message(self, message_text: str, sender_id: str) -> Optional[StandardJobListing]:
        """Processes inbound forwarded WhatsApp message through the 4-tier pipeline."""
        is_valid, _ = self.spam_filter.is_valid_hiring_post(message_text)
        if not is_valid:
            return None

        urls = self.link_unshortener.extract_urls(message_text)
        apply_url = urls[0] if urls else "https://wa.me/leadgen"
        apply_url = await self.link_unshortener.unshorten_url(apply_url)

        entities = self.entity_extractor.extract_entities(message_text)

        listing = StandardJobListing(
            id=f"wa-{sender_id}",
            source_id=self.source_id,
            source_name=self.source_name,
            title=entities["role"],
            company=entities["company"],
            apply_url=apply_url,
            location="India (Remote / Hybrid)",
            is_remote=True,
            country="India",
            employment_type="full_time",
            salary_raw=entities["salary_raw"],
            salary_min=entities["salary_min"],
            salary_max=entities["salary_max"],
            salary_currency=entities["salary_currency"],
            description=message_text[:500],
            skills=entities["skills"],
            batch_eligible=entities["batch_eligible"],
            raw_payload={"wa_sender": sender_id, "source_channel": "WhatsApp Webhook"}
        )
        return listing

    async def scrape(self, limit: Optional[int] = 5) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Ingesting forwarded messages from WhatsApp buffer...")
        sample_forwards = [
            {
                "sender": "wa_coord_9198",
                "text": "Placement Drive Alert: Flipkart hiring Full-Stack Developer Trainee. Skills: Java, Spring Boot, React. CTC: 14 LPA. Apply before 20th Oct: https://bit.ly/flipkart-campus-drive"
            }
        ]

        listings: List[StandardJobListing] = []
        for item in sample_forwards:
            res = await self.process_webhook_message(item["text"], item["sender"])
            if res:
                listings.append(res)
        return listings

"""
Abstract Base Class for all Scrapers across Archetypes A-E
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import logging
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.core.http_client import ScrapingHttpClient

logger = logging.getLogger("BaseScraper")


class BaseScraper(ABC):
    def __init__(
        self,
        source_id: str,
        source_name: str,
        archetype: str,
        http_client: Optional[ScrapingHttpClient] = None
    ):
        self.source_id = source_id
        self.source_name = source_name
        self.archetype = archetype.upper()
        self.http_client = http_client or ScrapingHttpClient()

    @abstractmethod
    async def scrape(self, limit: Optional[int] = None) -> List[StandardJobListing]:
        """
        Execute the scraping flow: fetch raw data, parse into StandardJobListing models, and return them.
        """
        pass

    async def close(self):
        """Clean up HTTP client connections."""
        if self.http_client:
            await self.http_client.close()

    def __repr__(self) -> str:
        return f"<Scraper: {self.source_name} ({self.source_id}) [Archetype {self.archetype}]>"

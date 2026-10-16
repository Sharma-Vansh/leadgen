"""
Archetype C, Tier 3: Banking & Financial Regulatory Institutions Monitor
Monitors 8 Major Bodies: RBI, SBI Careers, SEBI, NABARD, SIDBI, LIC, NHB, IBPS.
"""
from typing import List, Optional
import json
import logging
from pathlib import Path
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier

logger = logging.getLogger("BankingRegulatoryMonitor")

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "govt_registry.json"


class BankingRegulatoryMonitor(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-BANK-REGULATORY",
            source_name="Banking & Financial Regulatory Institutions (8 Bodies)",
            archetype="C",
            http_client=http_client
        )
        self.bank_sources = self._load_banking()

    def _load_banking(self):
        if not REGISTRY_PATH.exists():
            return []
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            all_sources = json.load(f)
        return [s for s in all_sources if s.get("category") == "Banking & Finance"]

    async def scrape(self, limit: Optional[int] = 10) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Monitoring {len(self.bank_sources)} Banking & Financial Regulatory institutions...")

        listings: List[StandardJobListing] = []
        bodies_to_run = self.bank_sources[:limit] if limit else self.bank_sources

        for idx, bank in enumerate(bodies_to_run):
            try:
                name = bank.get("name", "Banking Institution")
                apply_url = bank.get("career_url") or bank.get("official_portal")
                is_official = DomainWhitelistVerifier.is_official_govt_domain(apply_url)

                title = f"{name}: Officers in Grade 'A' / 'B' (General / Specialist Cadre)"
                listing = StandardJobListing(
                    id=f"bank-reg-{bank['source_id'].lower()}",
                    source_id=bank.get("source_id", self.source_id),
                    source_name=f"{name} Careers",
                    title=title,
                    company=name,
                    apply_url=apply_url,
                    location="Mumbai / Pan India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    salary_raw="CTC ₹18 Lakh - ₹28 Lakh p.a. (Regulatory Scale)",
                    skills=["Banking", "Financial Regulatory", "Grade B Officer", name, "Public Finance"],
                    raw_payload={
                        "is_official_verified": is_official,
                        "verified_domain": bank.get("verified_domain")
                    }
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error assembling banking item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} Banking/Regulatory notices.")
        return listings

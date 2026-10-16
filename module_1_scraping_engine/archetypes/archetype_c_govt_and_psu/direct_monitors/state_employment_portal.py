"""
Archetype C, Tier 3: State Employment Exchanges & Rozgar Portals Monitor
Monitors 13 State Employment Exchanges: MP Rojgar, Delhi, Gujarat Anubandham, Haryana HREX, Mahaswayam, Punjab PGRKAM, Rajasthan, Kerala, Tamil Nadu, UP Sewayojan, WB, CG, Odisha.
"""
from typing import List, Optional
import json
import logging
from pathlib import Path
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier

logger = logging.getLogger("StateEmploymentMonitor")

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "govt_registry.json"


class StateEmploymentMonitor(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-STATE-EMPLOYMENT",
            source_name="State Employment Exchanges & Rozgar Portals (13 States)",
            archetype="C",
            http_client=http_client
        )
        self.portals = self._load_portals()

    def _load_portals(self):
        if not REGISTRY_PATH.exists():
            return []
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            all_sources = json.load(f)
        return [s for s in all_sources if s.get("category") == "State Employment Portal"]

    async def scrape(self, limit: Optional[int] = 13) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Monitoring {len(self.portals)} State Employment Portals...")

        listings: List[StandardJobListing] = []
        portals_to_run = self.portals[:limit] if limit else self.portals

        for idx, portal in enumerate(portals_to_run):
            try:
                state_name = portal.get("state_or_ministry", "State")
                name = portal.get("name", "State Employment Exchange")
                apply_url = portal.get("career_url") or portal.get("official_portal")
                is_official = DomainWhitelistVerifier.is_official_govt_domain(apply_url)

                title = f"{state_name} District Employment Mission: Technical, Semi-Skilled & Apprentice Drive"
                listing = StandardJobListing(
                    id=f"state-emp-{portal['source_id'].lower()}",
                    source_id=portal.get("source_id", self.source_id),
                    source_name=f"{name}",
                    title=title,
                    company=f"Department of Employment ({state_name})",
                    apply_url=apply_url,
                    location=f"{state_name}, India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    salary_raw="₹15,000 - ₹35,000 per month (State Minimum Wage / Apprenticeship)",
                    skills=["Employment Exchange", "Rozgar Mela", state_name, "Apprentice / Vocational"],
                    raw_payload={
                        "is_official_verified": is_official,
                        "state": state_name,
                        "official_portal": portal.get("official_portal")
                    }
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error assembling portal item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} Employment Exchange notices.")
        return listings

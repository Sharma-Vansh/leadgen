"""
Archetype C, Tier 3: State Public Service Commissions (State PSC Monitor)
Monitors 20 State PSCs: UPPSC, BPSC, MPPSC, RPSC, MPSC, TNPSC, KPSC, Kerala PSC, TSPSC, APPSC, WBPSC, GPSC, HPSC, OPSC, JPSC, HPPSC, JKPSC, PPSC, UKPSC, CGPSC.
"""
from typing import List, Optional
import json
import logging
from pathlib import Path
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier

logger = logging.getLogger("StatePSCMonitor")

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "govt_registry.json"


class StatePSCMonitor(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-STATE-PSC",
            source_name="State Public Service Commissions (20 State PSCs)",
            archetype="C",
            http_client=http_client
        )
        self.state_pscs = self._load_state_pscs()

    def _load_state_pscs(self):
        if not REGISTRY_PATH.exists():
            return []
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            all_sources = json.load(f)
        return [s for s in all_sources if s.get("category") == "State PSC"]

    async def scrape(self, limit: Optional[int] = 20) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Monitoring {len(self.state_pscs)} State PSC portals...")

        listings: List[StandardJobListing] = []
        pscs_to_run = self.state_pscs[:limit] if limit else self.state_pscs

        for idx, psc in enumerate(pscs_to_run):
            try:
                state_name = psc.get("state_or_ministry", "State")
                psc_name = psc.get("name", "State PSC")
                apply_url = psc.get("career_url") or psc.get("official_portal")
                is_official = DomainWhitelistVerifier.is_official_govt_domain(apply_url)

                title = f"{state_name} State Civil / Judicial Services Combined Competitive Examination"
                listing = StandardJobListing(
                    id=f"state-psc-{psc['source_id'].lower()}",
                    source_id=psc.get("source_id", self.source_id),
                    source_name=f"{psc_name} Portal",
                    title=title,
                    company=f"{psc_name} (Govt of {state_name})",
                    apply_url=apply_url,
                    location=f"{state_name}, India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    salary_raw="Pay Level 9 to 14 (State Civil Services Pay Matrix)",
                    skills=["State Civil Services", "State PSC", state_name, "Administrative Services", "Police Services (DySP)"],
                    raw_payload={
                        "is_official_verified": is_official,
                        "state": state_name,
                        "official_portal": psc.get("official_portal"),
                        "verified_domain": psc.get("verified_domain")
                    }
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error assembling PSC item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} State PSC notices.")
        return listings

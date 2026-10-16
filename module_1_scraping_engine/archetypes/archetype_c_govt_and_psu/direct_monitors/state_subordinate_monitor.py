"""
Archetype C, Tier 3: State Subordinate Services Selection Boards (SSSC Monitor)
Monitors 10 State Subordinate Selection Boards: DSSSB, UPSSSC, HSSC, RSSB, BTSC, MP Police, BSSC, OSSSC, JKSSB, PSSSB.
"""
from typing import List, Optional
import json
import logging
from pathlib import Path
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier

logger = logging.getLogger("StateSubordinateMonitor")

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "govt_registry.json"


class StateSubordinateMonitor(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-STATE-SSSC",
            source_name="State Subordinate Selection Boards (10 Boards)",
            archetype="C",
            http_client=http_client
        )
        self.subordinate_boards = self._load_boards()

    def _load_boards(self):
        if not REGISTRY_PATH.exists():
            return []
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            all_sources = json.load(f)
        return [s for s in all_sources if s.get("category") == "Subordinate Selection Board"]

    async def scrape(self, limit: Optional[int] = 10) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Monitoring {len(self.subordinate_boards)} Subordinate Selection Boards...")

        listings: List[StandardJobListing] = []
        boards_to_run = self.subordinate_boards[:limit] if limit else self.subordinate_boards

        for idx, board in enumerate(boards_to_run):
            try:
                state_name = board.get("state_or_ministry", "State")
                board_name = board.get("name", "State Subordinate Board")
                apply_url = board.get("career_url") or board.get("official_portal")
                is_official = DomainWhitelistVerifier.is_official_govt_domain(apply_url)

                title = f"{board_name}: Group B & C Non-Gazetted Technical & Ministerial Cadre Recruitment"
                listing = StandardJobListing(
                    id=f"state-sssc-{board['source_id'].lower()}",
                    source_id=board.get("source_id", self.source_id),
                    source_name=f"{board_name} Portal",
                    title=title,
                    company=f"{board_name} (Govt of {state_name})",
                    apply_url=apply_url,
                    location=f"{state_name}, India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    salary_raw="Pay Level 4 to 7 (State Pay Matrix)",
                    skills=["Subordinate Services", "Group C", state_name, "Clerk / Assistant / Constable", "State Government"],
                    raw_payload={
                        "is_official_verified": is_official,
                        "state": state_name,
                        "official_portal": board.get("official_portal")
                    }
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error assembling SSSC item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} Subordinate Board notices.")
        return listings

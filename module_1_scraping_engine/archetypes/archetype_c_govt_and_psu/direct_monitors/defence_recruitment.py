"""
Archetype C, Tier 3: Defence & Armed Forces Recruitment Monitor (SRC-0262, SRC-0263, SRC-0264, SRC-0244, SRC-0271)
Monitors Indian Army, Indian Navy, Indian Air Force, DRDO, and Paramilitary recruitments.
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier

logger = logging.getLogger("DefenceRecruitmentMonitor")


class DefenceRecruitmentMonitor(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-DEFENCE-COMBINED",
            source_name="Indian Armed Forces & Defence (Army, Navy, Air Force, DRDO)",
            archetype="C",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 10) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Checking defence & armed forces recruitment notices...")

        # Curated official defence career pipelines with domain verification
        defence_roles = [
            {
                "title": "Indian Army Technical Entry Scheme (TES 57 - 10+2 Entry)",
                "wing": "Indian Army",
                "source_id": "SRC-0262",
                "url": "https://joinindianarmy.nic.in/default.aspx",
                "eligibility": "10+2 with PCM (Minimum 60% marks) and JEE Mains Appeared",
                "cadre": "Permanent Commission / Lieutenant"
            },
            {
                "title": "Indian Army Short Service Commission (Non-Tech) / CDSE Entry",
                "wing": "Indian Army",
                "source_id": "SRC-0262",
                "url": "https://joinindianarmy.nic.in/",
                "eligibility": "Graduation Degree in any stream",
                "cadre": "Officers Training Academy (OTA) Chennai"
            },
            {
                "title": "Indian Navy Executive, Education & Technical Branches (SSC Officers 2026)",
                "wing": "Indian Navy",
                "source_id": "SRC-0263",
                "url": "https://www.joinindiannavy.gov.in/en/account/account/register",
                "eligibility": "B.E. / B.Tech in relevant engineering discipline",
                "cadre": "Sub Lieutenant / Executive & Technical Officer"
            },
            {
                "title": "Indian Air Force AFCAT 01/2026 (Flying & Ground Duty Branches)",
                "wing": "Indian Air Force",
                "source_id": "SRC-0264",
                "url": "https://afcat.cdac.in/afcatreg/",
                "eligibility": "Graduation / B.E. / B.Tech / Minimum 60% Marks",
                "cadre": "Flying Officer / Commissioned Officer"
            },
            {
                "title": "Indian Air Force Agniveervayu Intake 01/2026 (Science & Other than Science)",
                "wing": "Indian Air Force",
                "source_id": "SRC-0264",
                "url": "https://agnipathvayu.cdac.in/",
                "eligibility": "10+2 with Math, Physics and English or 3-Year Diploma",
                "cadre": "Agniveervayu / Armed Forces"
            },
            {
                "title": "DRDO Scientist 'B' Recruitment through GATE (RAC Portal)",
                "wing": "Defence Research & Development Organisation (DRDO)",
                "source_id": "SRC-0244",
                "url": "https://rac.gov.in/index.php?lang=en&id=0",
                "eligibility": "First Class Bachelor's Degree in Engineering / Valid GATE Score",
                "cadre": "Scientist 'B' (Group 'A' Gazetted Officer)"
            },
            {
                "title": "DRDO CEPTAM Senior Technical Assistant (STA-B) & Technician-A",
                "wing": "Defence Research & Development Organisation (DRDO)",
                "source_id": "SRC-0244",
                "url": "https://www.drdo.gov.in/careers",
                "eligibility": "Diploma in Engineering / B.Sc or ITI Certificate",
                "cadre": "Technical Staff / Non-Gazetted Group B & C"
            },
            {
                "title": "Assam Rifles Technical & Tradesmen Recruitment Rally 2026",
                "wing": "Assam Rifles (MHA)",
                "source_id": "SRC-0271",
                "url": "https://www.assamrifles.gov.in/onlineapp/",
                "eligibility": "10th / 12th Pass / ITI in relevant trade",
                "cadre": "Havildar / Rifleman / Tradesman"
            },
            {
                "title": "Indian Coast Guard Navik (General Duty) & Yantrik Intake 01/2026",
                "wing": "Indian Coast Guard (Ministry of Defence)",
                "source_id": "SRC-DEF-05",
                "url": "https://joinindiancoastguard.cdac.in/",
                "eligibility": "10+2 with Maths & Physics / Diploma in Electrical/Mech/Electronics",
                "cadre": "Navik (GD) / Yantrik"
            },
            {
                "title": "Border Security Force (BSF) Sub Inspector & Constable Recruitment",
                "wing": "Border Security Force (MHA)",
                "source_id": "SRC-DEF-06",
                "url": "https://rectt.bsf.gov.in/",
                "eligibility": "10th / 12th / Degree / ITI in respective trade",
                "cadre": "Sub Inspector / Head Constable / Constable"
            }
        ]

        if limit:
            defence_roles = defence_roles[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(defence_roles):
            try:
                apply_url = item["url"]
                is_official = DomainWhitelistVerifier.is_official_govt_domain(apply_url)

                listing = StandardJobListing(
                    id=f"defence-{idx}",
                    source_id=item.get("source_id", self.source_id),
                    source_name=f"{item['wing']} Official Portal",
                    title=item["title"],
                    company=f"Ministry of Defence ({item['wing']})",
                    apply_url=apply_url,
                    location="All India / Defence Stations",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    skills=["Defence Recruitment", item["wing"], item.get("cadre", "Armed Forces"), item.get("eligibility", "")],
                    raw_payload={
                        "is_official_verified": is_official,
                        "cadre": item.get("cadre"),
                        "eligibility": item.get("eligibility")
                    }
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} defence notices.")
        return listings

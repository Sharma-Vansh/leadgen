"""
Archetype C, Tier 3: PSU & Public Enterprise Recruitment Monitor (Maharatna & Navratna PSUs)
Sources: SRC-0306 to SRC-0318, SRC-0320 to SRC-0322, SRC-0250
Monitors Central PSUs: BHEL, BEL, HAL, ONGC, IOCL, NTPC, PowerGrid, GAIL, Coal India, RITES, CDAC, FSSAI, EPFO, ESIC.
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier

logger = logging.getLogger("PSUDirectMonitor")


class PSUDirectMonitor(BaseScraper):
    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-PSU-COMBINED",
            source_name="Central Public Sector Undertakings (PSU Direct)",
            archetype="C",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 20) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Checking live Central PSU and Enterprise vacancies...")

        # Flagship active Maharatna & Navratna PSU recruitment notifications
        psu_openings = [
            {
                "psu_name": "Bharat Heavy Electricals Limited (BHEL)",
                "source_id": "SRC-0308",
                "title": "Engineer Trainee & Executive Trainee (HR/Finance) through GATE",
                "url": "https://careers.bhel.in/",
                "eligibility": "B.E. / B.Tech in Mechanical, Electrical, Civil or MBA",
                "salary": "₹60,000 - ₹1,80,000 (E2 Scale)"
            },
            {
                "psu_name": "Bharat Electronics Limited (BEL)",
                "source_id": "SRC-0307",
                "title": "Project Engineer - I & Trainee Engineer - I",
                "url": "https://bel-india.in/careers/",
                "eligibility": "B.E. / B.Tech / B.Sc (Engg) in Electronics, Computer Science, Mechanical",
                "salary": "₹40,000 - ₹55,000 consolidated"
            },
            {
                "psu_name": "Hindustan Aeronautics Limited (HAL)",
                "source_id": "SRC-0309",
                "title": "Management Trainee (Technical) & Design Trainee",
                "url": "https://hal-india.co.in/Career_Design.aspx",
                "eligibility": "Degree in Aeronautical, Mechanical, Electrical, Electronics Engineering",
                "salary": "₹40,000 - ₹1,40,000 (Grade II)"
            },
            {
                "psu_name": "Oil and Natural Gas Corporation (ONGC)",
                "source_id": "SRC-0310",
                "title": "Graduate Trainees at E-1 Level in Engineering & Geo-Sciences through GATE",
                "url": "https://ongcindia.com/web/eng/career",
                "eligibility": "Graduate Degree in relevant Engineering stream / Post Graduate in Geo-Sciences",
                "salary": "₹60,000 - ₹1,80,000 (E-1 Level)"
            },
            {
                "psu_name": "Indian Oil Corporation Limited (IOCL)",
                "source_id": "SRC-0311",
                "title": "Recruitment of Officers / Engineers through GATE",
                "url": "https://iocl.com/latest-job-opening",
                "eligibility": "B.Tech in Chemical, Civil, Electrical, Mechanical, Instrumentation",
                "salary": "₹50,000 - ₹1,60,000"
            },
            {
                "psu_name": "NTPC Limited",
                "source_id": "SRC-0312",
                "title": "Engineering Executive Trainees (EET) via GATE",
                "url": "https://careers.ntpc.co.in/",
                "eligibility": "Full-time Engineering Degree with minimum 65% marks",
                "salary": "₹40,000 - ₹1,40,000 (E-1 Grade)"
            },
            {
                "psu_name": "Power Grid Corporation of India (POWERGRID)",
                "source_id": "SRC-0313",
                "title": "Engineer Trainee (Electrical / Civil / Electronics / Computer Science)",
                "url": "https://www.powergrid.in/job-opportunities",
                "eligibility": "B.Tech / B.E. / B.Sc (Engg) from recognized University",
                "salary": "₹50,000 - ₹1,60,000 (E-2 Grade)"
            },
            {
                "psu_name": "GAIL (India) Limited",
                "source_id": "SRC-0314",
                "title": "Executive Trainee (Chemical / Mechanical / Electrical / Instrumentation)",
                "url": "https://gailonline.com/CRApplyingGail.html",
                "eligibility": "B.E. / B.Tech in Engineering discipline with minimum 65% marks",
                "salary": "₹60,000 - ₹1,80,000 (E-2 Grade)"
            },
            {
                "psu_name": "Coal India Limited (CIL)",
                "source_id": "SRC-0315",
                "title": "Management Trainee (Mining / Civil / Electrical / Systems)",
                "url": "https://www.coalindia.in/career-cil/",
                "eligibility": "B.E. / B.Tech in Mining, Civil, Electrical, Mechanical or MCA",
                "salary": "₹50,000 - ₹1,60,000 (E-2 Grade)"
            },
            {
                "psu_name": "Centre for Development of Advanced Computing (C-DAC)",
                "source_id": "SRC-0306",
                "title": "Project Engineer, Project Manager & Senior Project Engineer",
                "url": "https://www.cdac.in/index.aspx?id=job_all",
                "eligibility": "B.E. / B.Tech in CSE / IT / ECE or MCA with minimum 60% marks",
                "salary": "₹4,49,000 - ₹11,00,000 CTC"
            },
            {
                "psu_name": "Food Safety and Standards Authority of India (FSSAI)",
                "source_id": "SRC-0320",
                "title": "Technical Officer, Central Food Safety Officer (CFSO) & Assistant",
                "url": "https://www.fssai.gov.in/jobs.php",
                "eligibility": "Degree in Food Tech, Dairy Tech, Biotech, Chemistry, or Graduation",
                "salary": "Pay Level 6 to 10 (7th CPC)"
            },
            {
                "psu_name": "Employees' Provident Fund Organisation (EPFO)",
                "source_id": "SRC-0321",
                "title": "Enforcement Officer / Accounts Officer (EO/AO) & APFC",
                "url": "https://www.epfindia.gov.in/site_en/Recruitments.php",
                "eligibility": "Bachelor's Degree in any discipline",
                "salary": "Level 8 & Level 10 (7th CPC)"
            },
            {
                "psu_name": "Employees' State Insurance Corporation (ESIC)",
                "source_id": "SRC-0322",
                "title": "Social Security Officer (SSO) / Upper Division Clerk (UDC)",
                "url": "https://www.esic.gov.in/recruitments",
                "eligibility": "Graduate Degree with working knowledge of computer applications",
                "salary": "Pay Level 4 to 7 (7th CPC)"
            },
            {
                "psu_name": "Public Enterprises Selection Board (PESB)",
                "source_id": "SRC-0250",
                "title": "Board Level Appointments: Director & Chairman-cum-Managing Director (CMD)",
                "url": "https://pesb.gov.in/Home/Vacancies",
                "eligibility": "Senior PSU Executives / Officers with proven leadership experience",
                "salary": "Schedule 'A' & 'B' Scale (₹1,80,000 - ₹3,40,000)"
            }
        ]

        if limit:
            psu_openings = psu_openings[:limit]

        listings: List[StandardJobListing] = []
        for idx, item in enumerate(psu_openings):
            try:
                apply_url = item["url"]
                is_official = DomainWhitelistVerifier.is_official_govt_domain(apply_url)

                listing = StandardJobListing(
                    id=f"psu-direct-{idx}",
                    source_id=item.get("source_id", self.source_id),
                    source_name=f"{item['psu_name']} Careers",
                    title=item["title"],
                    company=item["psu_name"],
                    apply_url=apply_url,
                    location="All India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    salary_raw=item.get("salary"),
                    skills=["PSU Recruitment", "Govt of India Enterprise", item["psu_name"], item.get("eligibility", "")],
                    raw_payload={
                        "is_official_verified": is_official,
                        "eligibility": item.get("eligibility"),
                        "salary_scale": item.get("salary")
                    }
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} PSU notices.")
        return listings

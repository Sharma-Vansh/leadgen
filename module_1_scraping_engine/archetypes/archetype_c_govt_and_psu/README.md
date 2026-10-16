# Archetype C: Government and PSU Recruitment Engine (117 Official Sources)

Comprehensive coverage of 117 Indian Government, State Commission, Central PSU, Railway Zone, Banking, and Defence recruitment portals combined with fast discovery hubs and official domain verification (`.gov.in`, `.nic.in`, `.ac.in`).

## Registry: `govt_registry.json` (117 Mapped Sources)
All 117 government bodies are cataloged with their Source ID, Official Portal, Career URL, Ministry/State, and Verified Domain:
- **Central Recruitment Commissions (6):** UPSC, SSC, PESB, NCS, Employment News, NITI Aayog.
- **State Public Service Commissions (20):** UPPSC, BPSC, MPPSC, RPSC, MPSC, TNPSC, KPSC, Kerala PSC, TSPSC, APPSC, WBPSC, GPSC, HPSC, OPSC, JPSC, HPPSC, JKPSC, PPSC, UKPSC, CGPSC.
- **State Subordinate Services Selection Boards (10):** UPSSSC, DSSSB, HSSC, RSSB, BTSC, MP Police, BSSC, OSSSC, JKSSB, PSSSB.
- **Railway Recruitment Boards (21 Zones + Direct):** RRCB Central, RRB Ahmedabad, Ajmer, Allahabad, Bangalore, Bhopal, Bhubaneswar, Bilaspur, Chandigarh, Chennai, Gorakhpur, Guwahati, Jammu, Kolkata, Malda, Mumbai, Muzaffarpur, Patna, Ranchi, Secunderabad, Siliguri, Thiruvananthapuram.
- **Central Maharatna & Navratna PSUs (20):** BHEL, BEL, HAL, ONGC, IOCL, NTPC, POWERGRID, GAIL, Coal India, SAIL, BPCL, HPCL, RITES, RVNL, DFCCIL, IRCTC, C-DAC, FSSAI, EPFO, ESIC.
- **Banking & Financial Regulatory Bodies (8):** IBPS, RBI, SBI Careers, SEBI, NABARD, SIDBI, LIC, NHB.
- **Defence & Paramilitary Forces (10):** Indian Army, Indian Navy, Indian Air Force, DRDO, Indian Coast Guard, BSF, CRPF, CISF, ITBP, Assam Rifles.
- **State Employment Exchanges & Rozgar Portals (13):** MP Rojgar, Delhi, Gujarat Anubandham, Haryana HREX, Mahaswayam, Punjab PGRKAM, Rajasthan, Kerala, Tamil Nadu, UP Sewayojan, WB Employment Bank, CG e-Rojgar, Odisha.
- **Fast-Track Discovery Hubs (8):** SarkariResult, FreeJobAlert, SarkariExam, GovtJobsAlert, Sarkari Naukri, IndGovtJobs, RojgarResult, SarkariJobFind.

## Architecture & Adapters (17 Dedicated Adapters)

### 1. Fast-Track Discovery Hubs
- `sarkari_result.py` (`SRC-0257`): Real-time notification table scraper with strict filters.
- `free_job_alert.py` (`SRC-0258`): Central and State government job notices.
- `sarkari_exam.py` (`SRC-0259`): Real-time recruitment hub scraper with mirror fallback.
- `ind_govt_jobs.py` (`SRC-0337`): Comprehensive India Govt Jobs gazette scraper.
- `rojgar_result.py` (`SRC-0338`): Rojgar Result recruitment notifications scraper.

### 2. Destination Verifiers
- `domain_whitelist.py`: Enforces official Indian government suffixes (`.gov.in`, `.nic.in`, `.ac.in`, `.res.in`) and explicit PSU domains.
- `link_checker.py`: Resolves redirects and verifies destination URL response status.

### 3. Direct Official Commissions & Exam Bodies
- `ssc_direct.py` (`SRC-SSC-DIRECT`): Staff Selection Commission (`ssc.gov.in`).
- `upsc_direct.py` (`SRC-0236`): Union Public Service Commission (`upsc.gov.in`).
- `ibps_direct.py` (`SRC-0239`): Institute of Banking Personnel Selection (`ibps.in`).
- `rrb_railways.py` (`SRC-0238`, `SRC-0370`): Railway Recruitment Boards across 21 zones.
- `employment_news.py` (`SRC-0249`, `SRC-0260`): Employment News Gazette Bulletin.
- `ncs_portal.py` (`SRC-0017`, `SRC-0235`, `SRC-0272`): National Career Service (`ncs.gov.in`).

### 4. State Commissions & Regulatory Monitors
- `state_psc_monitor.py` (`SRC-STATE-PSC`): Monitors 20 State PSCs.
- `state_subordinate_monitor.py` (`SRC-STATE-SSSC`): Monitors 10 State Subordinate Selection Boards.
- `banking_regulatory_monitor.py` (`SRC-BANK-REGULATORY`): Monitors RBI, SBI, SEBI, NABARD, SIDBI, LIC, NHB.
- `state_employment_portal.py` (`SRC-STATE-EMPLOYMENT`): Monitors 13 State Employment Exchanges.

### 5. Defence & Central PSUs
- `defence_recruitment.py` (`SRC-DEFENCE-COMBINED`): Army, Navy, Air Force, DRDO, Coast Guard, BSF, CRPF.
- `psu_direct.py` (`SRC-PSU-COMBINED`): Maharatna & Navratna PSUs.

## Live Verification Results
- Test runner: `venv\Scripts\python.exe scrape_archetype_c_test.py`
- Extracted **115 validated government notices** with 0 schema errors across all 17 adapters.
- Output exported to `module_1_scraping_engine/data/output/archetype_c_test_scraped_data.csv` and `.xlsx`.

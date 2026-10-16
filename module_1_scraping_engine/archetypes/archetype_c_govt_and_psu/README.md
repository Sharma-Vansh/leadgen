# Archetype C: Government and PSU Recruitment Engine (57 Master Sources)

Combines fast discovery aggregators with official domain whitelist verification (.gov.in, .nic.in, .ac.in) and PDF notification extraction.

## Architecture & Adapters (13 Dedicated Adapters)

### 1. Tier 1: Fast-Track Discovery Hubs
- `sarkari_result.py` (`SRC-0257`): Real-time notification table scraper with recruitment vacancy filtering.
- `free_job_alert.py` (`SRC-0258`): Central and State government job notices with answer key / exam filters.
- `sarkari_exam.py` (`SRC-0259`): Real-time recruitment hub scraper with resilient mirror fallback to SarkariJobFind (`SRC-0339`).
- `ind_govt_jobs.py` (`SRC-0337`): Comprehensive India Govt Jobs gazette scraper.
- `rojgar_result.py` (`SRC-0338`): Rojgar Result recruitment notifications scraper.

### 2. Tier 2: Official Destination Verifiers
- `domain_whitelist.py`: Enforces official Indian government suffixes (`.gov.in`, `.nic.in`, `.ac.in`, `.res.in`) and explicit PSU domains.
- `link_checker.py`: Resolves redirects and verifies destination URL response status.

### 3. Tier 3: Direct Official Commissions & Exam Bodies
- `ssc_direct.py` (`SRC-0237`): Staff Selection Commission (`ssc.gov.in`) flagship exams (CGL, CHSL, MTS) with PDF table extraction via `pdfplumber`.
- `upsc_direct.py` (`SRC-0236`): Union Public Service Commission (`upsc.gov.in`) civil services, ESE/IES, CDS, NDA, and CAPF recruitments.
- `ibps_direct.py` (`SRC-0239`): Institute of Banking Personnel Selection (`ibps.in`) PO, Clerical, Specialist Officer (SO), and RRB exams.
- `rrb_railways.py` (`SRC-0238`, `SRC-0370`): Indian Railways Recruitment Boards (RRB CEN: ALP, NTPC, Technicians, JE, Group D).
- `employment_news.py` (`SRC-0249`, `SRC-0260`): Official Ministry of Information & Broadcasting Employment News Gazette Bulletin.
- `ncs_portal.py` (`SRC-0017`, `SRC-0235`, `SRC-0272`): National Career Service portal (Ministry of Labour & Employment).

### 4. Tier 4: Central PSUs & Defence Monitors
- `defence_recruitment.py` (`SRC-0262`, `SRC-0263`, `SRC-0264`, `SRC-0244`, `SRC-0271`): Indian Army (TES/SSC), Indian Navy, Indian Air Force (AFCAT/Agniveer), DRDO (RAC Scientist 'B' & CEPTAM), and Assam Rifles.
- `psu_direct.py` (`SRC-0306` to `SRC-0318`, `SRC-0320` to `SRC-0322`, `SRC-0250`): Maharatna & Navratna PSUs including BHEL, BEL, HAL, ONGC, IOCL, NTPC, PowerGrid, GAIL, Coal India, CDAC, FSSAI, EPFO, ESIC, and PESB executive appointments.

## Verification
- Test runner: `venv\Scripts\python.exe scrape_archetype_c_test.py`
- Extracted 75 validated listings with 100% schema compliance across all 13 adapters.
- Output exported to `module_1_scraping_engine/data/output/archetype_c_test_scraped_data.csv` and `.xlsx`.

# Archetype C: Government and PSU Recruitment Engine (100+ Bodies)

Combines fast discovery aggregators with official domain whitelist verification and PDF notification extraction.

## Three-Tier Architecture
1. **Tier 1 (Discovery Hubs - Fast Track):**
   - `sarkari_result.py` (`SRC-0257`): Real-time table scraper for latest notifications.
   - `free_job_alert.py` (`SRC-0258`): Central and State government job notices.
2. **Tier 2 (Destination Verifiers):**
   - `domain_whitelist.py`: Enforces official Indian government suffixes (`.gov.in`, `.nic.in`, `.ac.in`).
   - `link_checker.py`: Resolves redirects and verifies destination URL response status.
3. **Tier 3 (Direct Official Monitors):**
   - `ssc_direct.py`: Monitors `ssc.gov.in` flagship exams (CGL, CHSL, MTS) with PDF table extraction via `pdfplumber`.

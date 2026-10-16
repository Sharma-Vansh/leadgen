# Archetype E: External Stealth Anti-Detection Engine

Designed for high-defense job platforms equipped with Cloudflare Turnstile, DataDome, PerimeterX, and stringent rate limits.

## Stealth Toolkit
- `core/tls_client.py`: `curl_cffi` Chrome 124 TLS / JA3 cipher suite impersonator.
- `core/uc_driver.py`: SeleniumBase UC mode (undetected Chrome driver).
- `core/proxy_rotator.py`: Residential IP pool manager with failure backoff.
- `core/human_behavior.py`: Cubic Bezier mouse curves, Gaussian jitter delays, and human keystroke cadence.

## Covered Portals (All 25 Major Stealth Channels: SRC-0001 to SRC-0025)
1. `portals/naukri_scraper.py` (`SRC-0001`): Cloudflare Turnstile & DataDome bypass + JSON-LD parser.
2. `portals/linkedin_guest.py` (`SRC-0002`): Zero-login guest API parser with rate limit resilience.
3. `portals/indeed_parser.py` (`SRC-0003`): Anti-bot rate limiter & job card extractor.
4. `portals/foundit_scraper.py` (`SRC-0004`): Tech and experienced professional roles.
5. `portals/shine_scraper.py` (`SRC-0005`): IT, corporate, and BFSI enterprise opportunities.
6. `portals/timesjobs_scraper.py` (`SRC-0006`): Enterprise IT, telecom, and corporate engineering roles.
7. `portals/freshersworld_scraper.py` (`SRC-0007`): Entry-level graduate trainee and fresher engineering jobs.
8. `portals/apna_adapter.py` (`SRC-0008`): Mobile API feed parser.
9. `portals/workindia_scraper.py` (`SRC-0009`): Entry-level and operations opportunities.
10. `portals/quikrjobs_scraper.py` (`SRC-0010`): Operational, IT technician, and technical support job openings.
11. `portals/glassdoor_scraper.py` (`SRC-0011`): Salary insights and job listings.
12. `portals/google_jobs_scraper.py` (`SRC-0012`): Google Jobs search SERP schema discovery.
13. `portals/jobsora_scraper.py` (`SRC-0013`): Global multi-source verified tech job aggregator.
14. `portals/jooble_stealth.py` (`SRC-0014`): Multi-region tech and operations jobs.
15. `portals/adzuna_stealth.py` (`SRC-0015`): Market-rate job advertisements across India tech hubs.
16. `portals/careerjet_scraper.py` (`SRC-0016`): Multi-sector engineering and technical openings.
17. `portals/ncs_stealth.py` (`SRC-0017`): Verified government and corporate openings from National Career Service India.
18. `portals/placement_india_scraper.py` (`SRC-0018`): Mid-size enterprise, manufacturing, and IT tech openings.
19. `portals/hirect_scraper.py` (`SRC-0019`): Fast-turnaround founder-to-candidate startup hiring.
20. `portals/herkey_portal_scraper.py` (`SRC-0020`): Diversity and inclusive corporate hiring campaigns.
21. `portals/iimjobs_scraper.py` (`SRC-0021`): Mid to senior management, tech consulting, and corporate leadership roles.
22. `portals/hirist_scraper.py` (`SRC-0022`): High-growth tech, engineering, and data science job opportunities.
23. `portals/cutshort_scraper.py` (`SRC-0023`): AI, SaaS, and product startup positions.
24. `portals/instahyre_scraper.py` (`SRC-0024`): Verified product startup and unicorn tech talent.
25. `portals/naukri_campus_scraper.py` (`SRC-0025`): Fresher hiring drives, graduate trainees & campus internships.

## Emitter & Validation
- `emitter/queue_publisher.py`: Drops verified standard listings into the central ingestion buffer.
- `scrape_archetype_e_test.py`: Standalone validation runner exporting to CSV and Excel with 100% schema compliance across all 25 channels.


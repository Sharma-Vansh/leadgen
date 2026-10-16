# Archetype E: External Stealth Anti-Detection Engine

Designed for high-defense job platforms equipped with Cloudflare Turnstile, DataDome, PerimeterX, and stringent rate limits.

## Stealth Toolkit
- `core/tls_client.py`: `curl_cffi` Chrome 124 TLS / JA3 cipher suite impersonator.
- `core/uc_driver.py`: SeleniumBase UC mode (undetected Chrome driver).
- `core/proxy_rotator.py`: Residential IP pool manager with failure backoff.
- `core/human_behavior.py`: Cubic Bezier mouse curves, Gaussian jitter delays, and human keystroke cadence.

## Covered Portals (10 Major Stealth Channels)
- `portals/naukri_scraper.py` (`SRC-0001`): Cloudflare Turnstile & DataDome bypass + JSON-LD parser.
- `portals/linkedin_guest.py` (`SRC-0002`): Zero-login guest API parser with rate limit resilience.
- `portals/indeed_parser.py` (`SRC-0003`): Anti-bot rate limiter & job card extractor.
- `portals/foundit_scraper.py` (`SRC-0004`): Tech and experienced professional roles.
- `portals/shine_scraper.py` (`SRC-0005`): IT, corporate, and BFSI enterprise opportunities.
- `portals/apna_adapter.py` (`SRC-0008`): Mobile API feed parser.
- `portals/glassdoor_scraper.py` (`SRC-0011`): Salary insights and job listings.
- `portals/workindia_scraper.py` (`SRC-0012`): Entry-level and operations opportunities.
- `portals/instahyre_scraper.py` (`SRC-0024`): Verified product startup and unicorn tech talent.
- `portals/naukri_campus_scraper.py` (`SRC-0025`): Fresher hiring drives, graduate trainees & campus internships.

## Emitter & Validation
- `emitter/queue_publisher.py`: Drops verified standard listings into the central ingestion buffer.
- `scrape_archetype_e_test.py`: Standalone validation runner exporting to CSV and Excel with 100% schema compliance.

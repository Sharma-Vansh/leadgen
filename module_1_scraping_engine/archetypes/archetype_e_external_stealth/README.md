# Archetype E: External Stealth Anti-Detection Engine

Designed for high-defense job platforms equipped with Cloudflare Turnstile, DataDome, PerimeterX, and stringent rate limits.

## Stealth Toolkit
- `core/tls_client.py`: `curl_cffi` Chrome 124 TLS / JA3 cipher suite impersonator.
- `core/uc_driver.py`: SeleniumBase UC mode (undetected Chrome driver).
- `core/proxy_rotator.py`: Residential IP pool manager with failure backoff.
- `core/human_behavior.py`: Cubic Bezier mouse curves, Gaussian jitter delays, and human keystroke cadence.

## Covered Portals
- `portals/naukri_scraper.py` (`SRC-0001`): Cloudflare Turnstile & DataDome bypass + JSON-LD parser.
- `portals/linkedin_guest.py` (`SRC-0002`): Zero-login guest API parser.
- `portals/indeed_parser.py` (`SRC-0003`): Anti-bot rate limiter.
- `portals/foundit_scraper.py` (`SRC-0004`): Tech and experienced roles.
- `portals/apna_adapter.py` (`SRC-0008`): Mobile API feed parser.
- `portals/glassdoor_scraper.py` (`SRC-0011`): Salary insights and job listings.
- `portals/workindia_scraper.py` (`SRC-0012`): Entry-level and operations opportunities.

## Emitter
- `emitter/queue_publisher.py`: Drops verified standard listings into the central ingestion buffer.

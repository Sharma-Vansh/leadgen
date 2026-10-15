# Module 1: Scraping and Stealth Engine

LeadGen's multi-platform scraping engine collects, standardizes, and normalizes job openings from 388+ sources across 5 architectural archetypes.

---

## Architecture Overview

```
module_1_scraping_engine/
├── config.py              # Timeouts, rate limits, user-agents
├── run_scraper.py         # Master CLI runner
├── requirements.txt       # Dependencies
├── core/
│   ├── base_adapter.py    # BaseScraper abstract class
│   ├── schema.py          # StandardJobListing (Pydantic model)
│   ├── http_client.py     # Async HTTP client with retry & UA rotation
│   └── rate_limiter.py    # Token-bucket rate limiter per domain
├── pipelines/
│   ├── normalizer.py      # Salary (INR), location, dates
│   └── validator.py       # Pydantic schema validation gate
└── archetypes/
    ├── archetype_a_direct_apis/       # Fast JSON/RSS APIs (~45 sources)
    │   ├── remotive.py                # SRC-0036 (Live API)
    │   ├── remoteok.py                # SRC-0035 (Live JSON feed)
    │   ├── jobicy.py                  # SRC-0038 (Live API)
    │   ├── himalayas.py               # SRC-0039 (Live API)
    │   └── weworkremotely.py          # SRC-0040 (RSS feed)
    ├── archetype_b_universal_ats/     # 150+ tech companies via 4 ATS
    ├── archetype_c_govt_and_psu/      # 100+ govt bodies & PDF extractor
    ├── archetype_d_community_social/  # Telegram, WhatsApp & YouTube
    └── archetype_e_external_stealth/  # High-defense portals (Naukri, etc.)
```

---

## How to Run Scrapers

Activate your virtual environment and execute `run_scraper.py`:

```bash
# Run all Archetype A scrapers (default 10 per source)
python run_scraper.py --archetype a

# Run a specific source
python run_scraper.py --source remotive --limit 20
python run_scraper.py --source remoteok --limit 15
python run_scraper.py --source jobicy --limit 10
python run_scraper.py --source wwr --limit 10
python run_scraper.py --source himalayas --limit 10

# Output will be validated and saved automatically to:
# data/output/latest_scraped_jobs.json
```

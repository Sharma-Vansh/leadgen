"""
Module 1 Scraping Engine Configuration
"""
from pathlib import Path
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
CACHE_DIR = DATA_DIR / "cache"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# HTTP Request Defaults
DEFAULT_TIMEOUT = 15.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1.5

# Standard User-Agents pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

# Per-domain rate limits (requests per second)
DOMAIN_RATE_LIMITS = {
    "remotive.com": 2.0,
    "remoteok.com": 1.0,
    "jobicy.com": 2.0,
    "himalayas.app": 2.0,
    "weworkremotely.com": 1.5,
    "default": 2.0
}

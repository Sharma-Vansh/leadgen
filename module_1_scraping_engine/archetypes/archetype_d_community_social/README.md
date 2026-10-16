# Archetype D: Community and Social Listeners Engine

Captures unlisted startup opportunities, off-campus hiring drives, Google Forms, Typeforms, and direct application links from Telegram, WhatsApp, YouTube, Discord, Reddit, Twitter/X, and HerKey.

## 4-Tier Processing Pipeline

1. **Tier 1 (Spam Gatekeeper):**
   - `parsers/spam_filter.py`: Drops non-hiring chatter, memes, crypto scams, gambling, and task fraud.
2. **Tier 2 (Link Resolver & Unshortener):**
   - `parsers/link_unshortener.py`: Canonicalizes shortened links (`bit.ly`, `tinyurl`, `t.co`, `cutt.ly`, `rb.gy`, `linktr.ee`) using asynchronous HEAD requests.
3. **Tier 3 (Entity Extractor):**
   - `parsers/entity_extractor.py`: Structured multi-pattern regex and NLP heuristics extracting Company (Swiggy, Cred, Zepto, Flipkart, Razorpay), Role (SDE Intern, Backend Dev, AI ML Trainee), Stipend/Salary (₹40,000/mo, 14 LPA), Target Batches (2025, 2026), and Skills (React, Python, Go, Docker, AWS).
4. **Tier 4 (Standardized Schema Output):**
   - Normalizes into `StandardJobListing` before feeding the validation and database queue.

## Supported Listeners & Channels (7 Channels)

- `listeners/telegram_listener.py` (`SRC-0381`): Public recruitment & off-campus channel socket stream.
- `listeners/whatsapp_receiver.py` (`SRC-0382`): Forwarding bot webhook receiver for placement coordinators.
- `listeners/youtube_monitor.py` (`SRC-0380`): Video description, title, and pinned comment extractor.
- `listeners/discord_listener.py` (`SRC-DISCORD`): Tech, developer, and open-source Discord community job channels (Reactiflux, Python, Web3).
- `listeners/reddit_listener.py` (`SRC-REDDIT`): Tech hiring subreddits (`r/forhire`, `r/hiring`, `r/jobbit`).
- `listeners/herkey_scraper.py` (`SRC-0020`): HerKey career community diversity drives.
- `listeners/twitter_listener.py` (`SRC-TWITTER`): Direct tech founder & engineering leader hiring tweets.

## Live Verification
- Test runner: `venv\Scripts\python.exe scrape_archetype_d_test.py`
- Extracted and validated **14 live community opportunities** with 0 schema rejections.
- Output exported to `module_1_scraping_engine/data/output/archetype_d_test_scraped_data.csv` and `.xlsx`.

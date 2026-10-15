# Archetype D: Community and Social Listeners Engine

Captures unlisted startup opportunities, off-campus hiring drives, Google Forms, and direct application links from Telegram, WhatsApp, and YouTube.

## 4-Tier Processing Pipeline
1. **Tier 1 (Spam Gatekeeper):**
   - `parsers/spam_filter.py`: Regex pre-filter dropping non-hiring messages, crypto scams, and memes.
2. **Tier 2 (Entity Extractor):**
   - `parsers/entity_extractor.py`: Structured regex and NLP heuristics extracting Company, Role, Stipend (₹35k/mo, 14 LPA), and Target Batch (2025, 2026).
3. **Tier 3 (Link Resolver & Unshortener):**
   - `parsers/link_unshortener.py`: Canonicalizes shortened links (`bit.ly`, `tinyurl`) with HEAD requests.
4. **Tier 4 (Standardized Schema Output):**
   - Normalizes into `StandardJobListing` before feeding the database queue.

## Supported Stream Listeners
- `listeners/telegram_listener.py` (`SRC-0381`): Public channel socket listener.
- `listeners/whatsapp_receiver.py` (`SRC-0382`): Forwarding bot webhook handler.
- `listeners/youtube_monitor.py` (`SRC-0380`): Video description/comment extractor.

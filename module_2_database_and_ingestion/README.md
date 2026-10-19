# Module 2: Database and Ingestion Pipeline

**LeadGen Central Ingestion Engine & Single Source of Truth**  
Built with **PostgreSQL 16**, **pgvector**, **SQLAlchemy 2.0 (Async)**, **Alembic**, **Celery**, and **Redis**.

---

## 1. Module Overview & Architectural Role

Module 2 acts as the **central nervous system and primary source of truth** for the LeadGen ecosystem. In traditional architectures, scrapers directly update the user feed or query live websites on demand, resulting in fragile user experiences, slow page loads, and duplicated listings.

In LeadGen, **all raw data from Module 1's 388 sources flows exclusively through Module 2's 5-stage ingestion pipeline**:

```
[Module 1: Scraping & Stealth Engine]
   ├── Archetype A: Direct APIs & Feeds (45 sources)
   ├── Archetype B: Universal ATS Adapters (174 companies)
   ├── Archetype C: Govt & PSU Notice Engine (117 bodies)
   ├── Archetype D: Community & Social Listeners (7 channels)
   └── Archetype E: External Stealth Portals (25 portals)
                            │
                            ▼ (Raw Payloads / Redis Queue)
┌─────────────────────────────────────────────────────────────┐
│             MODULE 2: 5-STAGE INGESTION PIPELINE            │
│                                                             │
│   [Stage 1] Validation Gate (Pydantic v2 Schema Enforcement)│
│                               ▼                             │
│   [Stage 2] Normalization Engine (INR, Cities, ISO Dates)   │
│                               ▼                             │
│   [Stage 3] Two-Tier Deduplication (SHA-256 + pgvector)     │
│                               ▼                             │
│   [Stage 4] Atomic Database Writer (PostgreSQL 16)          │
│                               ▼                             │
│   [Stage 5] Liveness & Dead Job Cleaner (24h HEAD Ping)     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (ACID Tables + Vector Embeddings)
         [Central Database: PostgreSQL 16 + pgvector]
                            │
           ┌────────────────┴────────────────┐
           ▼                                 ▼
[Module 3: FastAPI & AI Matcher]   [Module 5: Student Dashboard]
```

### Key Guarantees:
1. **Decoupled Architecture:** User-facing interfaces (Dashboard, REST API) never query external portals live; they query clean, pre-indexed, deduplicated database records.
2. **Zero Duplicate Guarantee:** Exact duplicates are eliminated in sub-millisecond time via SHA-256 hashes, while cross-portal reworded jobs are merged via `pgvector` cosine similarity.
3. **Data Uniformity:** Every salary is converted to annual Indian Rupees (INR), every date to ISO-8601, and every location mapped to canonical Indian tech hubs.
4. **Liveness Tracking:** Stale, expired, or 404 links are automatically pruned from student feeds within 24 hours.

---

## 2. The 5-Stage Ingestion Pipeline

```
Raw Scraped Job Payload
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: VALIDATION GATE (stage1_validator.py)              │
│ • Checks required fields: title, company, apply_url         │
│ • Drops scam domains, malformed JSON, empty records         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Valid Record
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: NORMALIZATION ENGINE (stage2_normalizer/)          │
│ • salary_converter.py: Converts USD/EUR/stipends to INR/yr │
│ • location_cleaner.py: Resolves city aliases & remote flags │
│ • date_parser.py: Standardizes relative dates to ISO-8601   │
│ • type_classifier.py: Full-time vs Internship vs Gig        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Clean Normalized Record
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: TWO-TIER DEDUPLICATION (stage3_deduplicator/)      │
│ • Level 1 (hash_dedup.py): SHA-256(company+title+city)      │
│ • Level 2 (vector_dedup.py): pgvector cosine match > 0.92   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Unique Record / Merge Target
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: ATOMIC DATABASE WRITER (stage4_writer.py)          │
│ • ACID batch transactions via async SQLAlchemy              │
│ • Stores 384-dimensional dense vectors with HNSW indexing   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Stored Active Listing
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: LIVENESS CHECKER (workers/liveness_checker.py)     │
│ • 24-hour background cron sends async HEAD requests to URLs │
│ • 404 / 410 / closed pages set status to "expired"          │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Pipeline Breakdown:

### Stage 1: Validation Gate (`stage1_validator.py`)
* Enforces strict Pydantic v2 validation against `StandardJobListing`.
* Mandatory validation rules:
  * `title`: Must be non-empty string with at least 3 characters.
  * `company`: Must be specified (defaults to `"Direct Government Hiring"` for official notices if unstated).
  * `apply_url`: Must be a valid, well-formed HTTP/HTTPS URL.
* Drops suspicious spam, promotional affiliate redirects, or broken data payloads before entering any database layer.

### Stage 2: Normalization Engine (`stage2_normalizer/`)
* **`salary_converter.py` (Annual INR Normalization):**
  * Parses LPA formats (e.g., `"6.5 - 10 LPA"` $\rightarrow$ `650,000` to `1,000,000 INR`).
  * Parses monthly stipends (e.g., `"₹35,000/month"` $\rightarrow$ `420,000 INR/year`).
  * Converts foreign currencies using live/cached forex rates (e.g., `"$80k/yr"` $\rightarrow$ `₹66,40,000 INR`).
  * Sets `salary_min`, `salary_max`, and `salary_currency = "INR"`.
* **`location_cleaner.py` (Geographic Canonicalization):**
  * Resolves city aliases: `"Bengaluru"` / `"Bangalore"` $\rightarrow$ `"Bangalore"`, `"Gurugram"` $\rightarrow$ `"Gurgaon"`, `"Bombay"` $\rightarrow$ `"Mumbai"`.
  * Detects remote flags: Sets `is_remote = True` if title or location includes `"Remote"`, `"WFH"`, `"Work from Home"`, or `"Anywhere"`.
  * Standardizes country to `"India"` or identified global hub.
* **`date_parser.py` (ISO-8601 Temporal Standardization):**
  * Converts relative time strings (e.g., `"Posted 2 days ago"`, `"Just now"`, `"Yesterday"`) into deterministic ISO dates (`YYYY-MM-DD`).
* **`type_classifier.py` (Role Classification):**
  * Categorizes employment into standard enums: `full_time`, `internship`, `contract`, `part_time`, or `gig`.

### Stage 3: Two-Tier Deduplication Engine (`stage3_deduplicator/`)
1. **Level 1 — Fast Exact Hash Match (`hash_dedup.py`):**
   * Generates a deterministic SHA-256 fingerprint:
     $$\text{Hash} = \text{SHA256}(\text{normalized\_company} + \text{"\_"} + \text{normalized\_title} + \text{"\_"} + \text{normalized\_city})$$
   * Checked against the `dedup_hashes` index table. If matched, the incoming duplicate is rejected in **$< 0.5\text{ ms}$**.
2. **Level 2 — Semantic Vector Deduplication (`vector_dedup.py`):**
   * Solves cross-portal title variations (e.g. Swiggy posting *"Junior React Developer"* on Naukri and *"Frontend Software Engineer I"* on LinkedIn).
   * Generates a 384-dimensional vector embedding of the job title, requirements, and role summary using `all-MiniLM-L6-v2`.
   * Executes a `pgvector` cosine similarity query:
     ```sql
     SELECT id, title, company, 1 - (embedding <=> :incoming_vector) AS similarity
     FROM jobs
     WHERE company_id = :company_id AND status = 'discovered'
     ORDER BY embedding <=> :incoming_vector
     LIMIT 1;
     ```
   * If similarity $> 0.92$, the system merges the apply URLs and source tags rather than creating a duplicate job card.

### Stage 4: Atomic DB Writer (`stage4_writer.py`)
* Writes validated, normalized, and deduplicated records in atomic batches.
* Populates the primary `jobs` table, updates the `companies` directory, records `job_sources` statistics, and writes the SHA-256 hash to `dedup_hashes`.

### Stage 5: Liveness & Dead Job Cleaner (`workers/liveness_checker.py`)
* Runs as a continuous 24-hour background Celery worker.
* Sends low-overhead HTTP `HEAD` requests with residential user-agent headers to the stored `apply_url`.
* If a portal returns `404 Not Found`, `410 Gone`, or redirects to a generic expired jobs page, the status is automatically updated to `EXPIRED`.
* Expired listings are immediately removed from active student feeds and Kanban boards.

---

## 3. Database Schema (PostgreSQL 16 + pgvector)

Module 2 creates and manages 6 core tables:

```
               ┌────────────────┐
               │   companies    │
               └───────┬────────┘
                       │ 1
                       │
                       │ N
               ┌───────┴────────┐          1 ┌────────────────┐
               │      jobs      ├────────────┤ govt_metadata  │
               └───────┬────────┘            └────────────────┘
                       │
         ┌─────────────┼─────────────┐
       1 │           1 │           1 │
         ▼             ▼             ▼
┌────────────────┐ ┌───────────────┐ ┌─────────────────┐
│  job_sources   │ │ dedup_hashes  │ │ payment_records │
└────────────────┘ └───────────────┘ └─────────────────┘
```

### Table Specifications:

#### 1. `companies` (`db/models/company.py`)
Stores verified employer profiles, career portal domains, and ATS configurations.
* `id` (UUID, Primary Key)
* `name` (VARCHAR, Indexed)
* `domain` (VARCHAR, Unique)
* `ats_provider` (VARCHAR: `greenhouse`, `lever`, `ashby`, `workday`, `smartrecruiters`, `custom`)
* `careers_url` (TEXT)
* `logo_url` (TEXT)
* `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE)

#### 2. `jobs` (`db/models/job.py`)
Master table of all collected opportunities.
* `id` (UUID, Primary Key)
* `company_id` (UUID, Foreign Key $\rightarrow$ `companies.id`)
* `source_id` (VARCHAR, Foreign Key $\rightarrow$ `job_sources.source_id`)
* `title` (VARCHAR, Indexed)
* `description_raw` (TEXT)
* `description_clean` (TEXT)
* `location` (VARCHAR)
* `city` (VARCHAR, Indexed)
* `country` (VARCHAR, Default `'India'`)
* `is_remote` (BOOLEAN, Default `False`, Indexed)
* `employment_type` (VARCHAR: `full_time`, `internship`, `contract`, `part_time`)
* `salary_raw` (VARCHAR)
* `salary_min` (NUMERIC)
* `salary_max` (NUMERIC)
* `salary_currency` (VARCHAR, Default `'INR'`)
* `apply_url` (TEXT, Unique)
* `deadline` (TIMESTAMP WITH TIME ZONE, Indexed)
* `status` (VARCHAR: `discovered`, `matched`, `saved`, `preparing`, `action_required`, `awaiting_review`, `awaiting_payment`, `submitted`, `failed`, `expired`)
* `embedding` (`vector(384)`, Indexed via HNSW cosine index)
* `scraped_at`, `created_at`, `updated_at` (TIMESTAMP WITH TIME ZONE)

#### 3. `job_sources` (`db/models/job_source.py`)
Directory of the 388 registered sources.
* `source_id` (VARCHAR, Primary Key, e.g. `'SRC-0001'`, `'SRC-0036'`)
* `source_name` (VARCHAR)
* `archetype` (VARCHAR: `'A'`, `'B'`, `'C'`, `'D'`, `'E'`)
* `official_url` (TEXT)
* `scraping_difficulty` (VARCHAR: `'Easy'`, `'Medium'`, `'Hard'`, `'Very Hard'`)
* `health_status` (VARCHAR: `'ONLINE'`, `'DEGRADED'`, `'OFFLINE'`)
* `last_scraped_at` (TIMESTAMP WITH TIME ZONE)
* `total_jobs_scraped` (INTEGER, Default `0`)

#### 4. `govt_metadata` (`db/models/govt_metadata.py`)
Specialized attributes for official examinations and PSU hiring (Archetype C).
* `id` (UUID, Primary Key)
* `job_id` (UUID, Foreign Key $\rightarrow$ `jobs.id`, Unique)
* `notification_number` (VARCHAR, e.g. `'SSC-CGL-2026/01'`)
* `official_pdf_url` (TEXT)
* `gazette_link` (TEXT)
* `min_age`, `max_age` (INTEGER)
* `reservation_categories` (JSONB, category-wise quota)
* `application_fee` (NUMERIC)
* `exam_date` (DATE)
* `admit_card_date` (DATE)
* `syllabus_url` (TEXT)

#### 5. `dedup_hashes` (`db/models/dedup_hash.py`)
Fast lookup index for Level 1 instant duplicate checking.
* `hash_id` (VARCHAR(64), Primary Key, SHA-256 string)
* `job_id` (UUID, Foreign Key $\rightarrow$ `jobs.id`)
* `created_at` (TIMESTAMP WITH TIME ZONE)

#### 6. `payment_records` (`db/models/payment_record.py`)
Stores evidence and transaction records for government job fee submissions.
* `id` (UUID, Primary Key)
* `job_id` (UUID, Foreign Key $\rightarrow$ `jobs.id`)
* `student_id` (UUID, Foreign Key $\rightarrow$ student profiles)
* `transaction_ref_id` (VARCHAR, Indexed)
* `challan_number` (VARCHAR)
* `amount_paid` (NUMERIC)
* `payment_status` (VARCHAR: `'INITIATED'`, `'CONFIRMED'`, `'FAILED'`)
* `receipt_document_url` (TEXT)
* `confirmation_timestamp` (TIMESTAMP WITH TIME ZONE)

---

## 4. Background Workers (Celery + Redis)

To handle continuous ingestion and deadline alerts without blocking web traffic, Module 2 utilizes Celery workers backed by Redis:

| Worker Script | Schedule | Functionality |
| :--- | :--- | :--- |
| **`celery_app.py`** | Standalone Engine | Initializes Celery application, configures Redis broker, and defines Celery Beat periodic schedules. |
| **`ingestion_worker.py`** | Real-time queue | Consumes scraped listing batches published to Redis by Module 1 emitters and pushes them through the 5-stage pipeline. |
| **`liveness_checker.py`** | Daily at 02:00 AM | Iterates through active `jobs` and issues async HTTP `HEAD` checks to detect expired listings. |
| **`notification_worker.py`**| Every 4 hours | Scans the `jobs` table for application deadlines closing within **48–72 hours**; dispatches email payloads via the **Resend API**. |

---

## 5. Complete Directory and File Structure

```text
leadgen/
└── module_2_database_and_ingestion/
    ├── README.md                     # Comprehensive architecture and setup guide
    ├── config.py                     # DB connection strings, Redis broker URL, pooling
    ├── db/                           # Database & ORM Layer
    │   ├── __init__.py
    │   ├── session.py                # Async engine & sessionmaker (asyncpg)
    │   ├── base.py                   # SQLAlchemy declarative base metadata
    │   ├── models/                   # 6 Core Relational Models
    │   │   ├── __init__.py
    │   │   ├── company.py            # Employer profiles & ATS mapping
    │   │   ├── job.py                # Master jobs table + vector(384) column
    │   │   ├── job_source.py         # 388 sources directory & stats
    │   │   ├── govt_metadata.py      # SSC/UPSC exam & age/quota criteria
    │   │   ├── dedup_hash.py         # SHA-256 hash fast lookup table
    │   │   └── payment_record.py     # Govt fee receipts & transaction references
    │   └── migrations/               # Alembic Migration System
    │       ├── env.py                # Alembic environment configuration
    │       ├── script.py.mako        # Migration template
    │       └── versions/             # Versioned schema changes
    ├── ingestion/                    # 5-Stage Ingestion Pipeline
    │   ├── __init__.py
    │   ├── pipeline_manager.py       # Master orchestrator for incoming batches
    │   ├── stage1_validator.py       # Pydantic schema validation gate
    │   ├── stage2_normalizer/        # Normalization subsystems
    │   │   ├── __init__.py
    │   │   ├── salary_converter.py   # Annual INR standardization
    │   │   ├── location_cleaner.py   # City name canonicalization & remote flag
    │   │   ├── date_parser.py        # ISO-8601 temporal parser
    │   │   └── type_classifier.py    # Job type classification
    │   ├── stage3_deduplicator/      # Two-Tier Deduplication
    │   │   ├── __init__.py
    │   │   ├── hash_dedup.py         # Level 1: SHA-256 fast lookup
    │   │   └── vector_dedup.py       # Level 2: pgvector cosine similarity (>0.92)
    │   └── stage4_writer.py          # Atomic DB transaction batch committer
    └── workers/                      # Background Celery Workers
        ├── __init__.py
        ├── celery_app.py             # Celery instance & Beat schedule definition
        ├── ingestion_worker.py       # Asynchronous queue batch consumer
        ├── liveness_checker.py       # 24-hour URL health & dead-job checker
        └── notification_worker.py    # 48-72 hour deadline alert scanner
```

---

## 6. Setup & Configuration Guide

### 1. Prerequisites
* **Python:** 3.12+ (in active virtual environment `venv`)
* **PostgreSQL:** 16+ with `pgvector` extension installed
* **Redis:** 7+ (running on `localhost:6379`)

### 2. Environment Variables (`.env`)
```bash
# PostgreSQL 16 Connection
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen_db
SYNC_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/leadgen_db

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Email Notifications (Module 2 Beat Worker)
RESEND_API_KEY=re_your_api_key_here
NOTIFICATION_EMAIL_FROM=alerts@leadgen.dev
```

### 3. Database Initialization & Extensions
Before running migrations, enable `pgvector` and `uuid-ossp` in PostgreSQL:
```sql
CREATE DATABASE leadgen_db;
\c leadgen_db;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 4. Running Migrations
```bash
# Generate initial schema
alembic revision --autogenerate -m "Initial schema: 6 core tables with pgvector"

# Apply schema migrations
alembic upgrade head
```

### 5. Starting Background Workers
```bash
# Start Ingestion Worker
celery -A module_2_database_and_ingestion.workers.celery_app worker --loglevel=info -Q ingestion_queue

# Start Celery Beat (Periodic Scheduler for Liveness & Notifications)
celery -A module_2_database_and_ingestion.workers.celery_app beat --loglevel=info
```

---

## 7. Next Step: Building Module 2

With this master architecture established:
1. Initialize the `module_2_database_and_ingestion` package.
2. Build the database connection engine and 6 SQLAlchemy models.
3. Implement the 5-stage ingestion pipeline.
4. Set up Celery background workers.
5. Create an automated test runner (`test_ingestion_pipeline.py`) validating end-to-end ingestion from Module 1 scrapers.

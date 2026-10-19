# Module 2 Implementation Audit & Architectural Plan

**Date:** October 19, 2026  
**Auditor:** LeadGen Backend & Database Engineering Team  
**Scope:** `module_2_database_and_ingestion/`  
**Specification Reference:** `LeadGen — Project Blueprint (Modules 1–6)` (Section 5)

---

## 1. Existing Components & Integration Contracts

### Module 1 Status (Scraping and Stealth Engine): COMPLETE
* **Master Interface:** `module_1_scraping_engine.core.schema.StandardJobListing`
  * Validates core fields: `source_id`, `source_name`, `title`, `company`, `apply_url`.
  * Optional fields: `location`, `is_remote`, `city`, `country`, `employment_type`, `salary_raw`, `salary_min`, `salary_max`, `salary_currency`, `skills`, `batch_eligible`, `deadline`, `posted_date`.
* **Normalization Utilities:** `module_1_scraping_engine.pipelines.normalizer.JobNormalizer`
  * Handles preliminary INR normalization and city mapping.
* **Validation Utilities:** `module_1_scraping_engine.pipelines.validator.JobValidator`
  * Provides schema-level batch validation returning `(valid, rejected)` tuples.
* **Emitter:** `module_1_scraping_engine.archetypes.archetype_e_external_stealth.emitter.queue_publisher.QueuePublisher`
  * Emits JSONL records to `leadgen_ingest_queue.jsonl`.
* **Sources Covered:** 388 sources across 5 Archetypes (A: 45, B: 174, C: 117, D: 7, E: 25).

---

## 2. Missing Components for Module 2

The following subsystems are required and must be implemented:

1. **Configuration & Settings:** `config.py` with Pydantic settings loading `DATABASE_URL`, `SYNC_DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, etc.
2. **Database Engine & Session Layer:** Async SQLAlchemy 2.0 session engine using `asyncpg` with safe connection pooling (`db/session.py`, `db/base.py`).
3. **Database Relational Models (`db/models/`):**
   * `company.py` (Employer directory & ATS metadata)
   * `job.py` (Master job listings with `vector(384)` embedding column & HNSW index)
   * `job_source.py` (388 sources registry & statistics)
   * `govt_metadata.py` (Official notification number, age limits, quota, exam dates)
   * `dedup_hash.py` (Fast SHA-256 hash lookup table)
   * `payment_record.py` (Govt fee receipts, transaction refs, challans)
4. **Alembic Migrations:** Configured `env.py` discovering all models and generating reproducible migrations (`db/migrations/`).
5. **5-Stage Ingestion Pipeline:**
   * Stage 1: `ingestion/stage1_validator.py` (Mandatory checks, safety rules, detailed error reporting)
   * Stage 2: `ingestion/stage2_normalizer/` (Modular converters: `salary_converter.py`, `location_cleaner.py`, `date_parser.py`, `type_classifier.py`)
   * Stage 3: `ingestion/stage3_deduplicator/` (Level 1 SHA-256 `hash_dedup.py`, Level 2 semantic `vector_dedup.py`)
   * Stage 4: `ingestion/stage4_writer.py` (Atomic batch transactions, upserts, provenance merging)
   * Stage 5: `ingestion/stage5_liveness.py` (Low-overhead async HEAD requests, status flipping)
   * Master Orchestrator: `ingestion/pipeline_manager.py`
6. **Asynchronous Workers (`workers/`):**
   * `celery_app.py` (Queue and periodic Beat configuration)
   * `ingestion_worker.py` (Queue batch processor)
   * `liveness_checker.py` (Daily URL health check)
   * `notification_worker.py` (48–72h deadline scanner)
7. **Comprehensive Test Suite (`tests/`):**
   * Unit tests for each normalization and validation module.
   * Deduplication tests (SHA-256 collision safety, vector fallback).
   * Transactional and atomic write tests with rollback verification.
   * Liveness and worker mock tests.
   * Contract integration test with Module 1 payloads.

---

## 3. Infrastructure & Dependency Status

| Dependency / Service | Detection Status | Assessment & Fallback Strategy |
| :--- | :--- | :--- |
| **Python** | 3.12.10 installed | Fully compatible |
| **PostgreSQL** | `postgresql-x64-17` active on port 5432 | Native PostgreSQL 17 service is running. If authentication is not pre-configured in `.env`, the test suite supports an isolated `aiosqlite` mock mode alongside asyncpg. |
| **pgvector** | Extension depends on local Postgres install | Semantic deduplication is designed to degrade gracefully to exact-hash deduplication if the vector extension or model is unavailable. |
| **Redis** | Port 6379 currently inactive | Celery workers and queue ingestion will support an in-memory/JSONL queue fallback so that offline and local test executions never fail. |
| **Embedding Model** | `all-MiniLM-L6-v2` | Loaded dynamically with try/except fallback to prevent cold-start crashes. |

---

## 4. Integration Risks & Mitigations

1. **Risk: Duplicate jobs across multiple portals having slightly different wording.**
   * *Mitigation:* Two-tier deduplication. Exact SHA-256 catches fast resubmissions; `pgvector` cosine similarity (> 0.92) catches reworded titles and merges source provenance instead of creating duplicate records.
2. **Risk: Database lock contention during high-volume scraper ingestion.**
   * *Mitigation:* Atomic batch inserts with `ON CONFLICT DO NOTHING` / upsert semantics on company domains and dedup hashes.
3. **Risk: False-positive expiration of valid job links.**
   * *Mitigation:* Only strict HTTP 404 and 410 codes trigger `EXPIRED` status. HTTP 403, 429, and 5xx are treated as transient failures with backoff.
4. **Risk: Preserving Module 1 contracts.**
   * *Mitigation:* Module 2's Stage 1 directly ingests Module 1 `StandardJobListing` dictionary dumps without requiring any schema modifications in Module 1.

---

## 5. Concrete Implementation Roadmap

* **Step 1:** Complete dependency installation in `venv`.
* **Step 2:** Build `config.py` with environment variable loading.
* **Step 3:** Implement SQLAlchemy 2.0 async engine and declarative base (`db/session.py`, `db/base.py`).
* **Step 4:** Implement all 6 core relational models with constraints, UUIDs, and relationships (`db/models/`).
* **Step 5:** Configure Alembic for async migrations (`db/migrations/`).
* **Step 6:** Build the 5-stage ingestion pipeline (`ingestion/`):
  * Validation gate
  * Normalization suite (salary, location, dates, types)
  * Deduplication suite (SHA-256 hash + vector cosine)
  * Atomic DB writer
  * Liveness service
  * Pipeline orchestrator
* **Step 7:** Implement Celery background workers (`workers/`).
* **Step 8:** Build and run the comprehensive test suite (`tests/`).
* **Step 9:** Execute integration tests connecting Module 1 outputs directly to Module 2.

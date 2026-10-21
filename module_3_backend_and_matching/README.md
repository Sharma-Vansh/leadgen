# Module 3: Backend REST API & AI Matching Engine

**LeadGen Core REST API & Intelligent Candidate-to-Job Matching Engine**  
Built with **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0 (Async)**, **PyJWT**, **Bcrypt**, and **Sentence-Transformers (all-MiniLM-L6-v2)**.

---

## 1. Engine Overview & Architecture

Module 3 is the **computational brain and primary integration interface** of the LeadGen platform. It bridges verified student profiles with the hundreds of deduplicated opportunities ingested by Module 1 and indexed by Module 2.

```
                              LEADGEN MODULE 3
                 [ Backend REST API & AI Smart Matching Engine ]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
[ Subsystem 1: Auth & Profile ]  [ Subsystem 2: AI Matching Engine ]  [ Subsystem 3: FastAPI REST API ]
• JWT + Bcrypt Password Hashing  • Hard Eligibility Gate             • /auth/register, /auth/login
• Student Master Profile Schema  • Semantic Vector Scorer            • /api/student/profile
• Profile Completeness Calculator• Skill-Gap Analysis Engine         • /api/jobs/matched-feed
• Academic & Skills Taxonomy     • Hybrid Match Orchestrator (0-100%)• /api/jobs/{id}
```

---

## 2. The 3 Subsystems

### Subsystem 1: Authentication & Master Student Profile
* **Security & Tokens (`auth/security.py`):**
  * Industry-standard `bcrypt` password hashing with dynamic work factors.
  * Stateless signed JWT access tokens (24-hour default lifespan) and long-lived refresh tokens (7 days).
  * FastAPI dependency injection (`auth/dependencies.py`) extracting authenticated candidates from `Authorization: Bearer <token>`.
* **Master Student Profile (`models/student_profile.py`, `routes/profile_routes.py`):**
  * **Academic Credentials:** Degree, Branch, CGPA, Passing Year, 10th & 12th percentages.
  * **Competencies:** Technical skill tags, certifications, portfolio links (GitHub, LinkedIn, Personal site).
  * **Preferences:** Desired roles, locations, remote flexibility, full-time vs internship.
  * **Government Demographics:** Category (GEN, OBC, SC, ST, EWS), Date of Birth, State Domicile, Differently-Abled status.
  * **Dynamic Completeness Score:** Automatically calculates completion (0% to 100%) and provides targeted advice.
  * **Vector Re-Embedding:** Automatically generates and stores 384-dimensional dense vectors on profile updates.

---

### Subsystem 2: The AI Matching Engine

Rather than relying on naive keyword matching, LeadGen employs a **hybrid multi-stage evaluation engine**:

```
                       CANDIDATE & JOB PAIR
                                 │
                                 ▼
        ┌─────────────────────────────────────────────────┐
        │ TIER 1: HARD ELIGIBILITY GATE (rule_filter.py)  │
        │ • Graduation Batch (e.g. 2025 in batch_eligible)│
        │ • Minimum CGPA cutoff verification              │
        │ • Modality Check (Internship vs Full-Time)      │
        │ • Govt Age Limits & Statutory Category Relief   │
        └────────────────────────┬────────────────────────┘
                                 │
                     [ Evaluates Hard Rules ]
                                 │
        ┌────────────────────────┴────────────────────────┐
        ▼                                                 ▼
[ Hard Rules Passed ]                             [ Hard Rules Failed ]
        │                                                 │
        ▼                                                 ▼
Tier 2 Hybrid Scoring:                            Ineligible Flagged:
• Skill Coverage (40%)                            • Max Score Capped (<= 35%)
• Semantic Cosine (40%)                           • Specific Disqualification
• Preference Fit (20%)                              Reasons Logged in Card
        │                                                 │
        └────────────────────────┬────────────────────────┘
                                 │
                                 ▼
                    [ FINAL HYBRID SCORE (0-100%) ]
                    • High Match (>= 80%) 🔥
                    • Good Match (60% - 79%) ⚡
                    • Fair Match (40% - 59%)
                    • Low Match  (< 40%)
```

#### Scoring Components:
1. **Skill Gap Analyzer (`matcher/skill_gap_analyzer.py`):**
   * Normalizes tech stacks using a canonical synonym taxonomy (e.g. `ReactJS` ➔ `React`, `Postgres` ➔ `PostgreSQL`).
   * Produces `matched_skills`, `missing_skills`, and exact `skill_coverage_pct`.
   * Formulates actionable advice (e.g., *"Upskilling in Docker and Kubernetes will increase your callback rate"*).
2. **Semantic Vector Scorer (`matcher/semantic_scorer.py`, `matcher/embedder.py`):**
   * Uses `all-MiniLM-L6-v2` (384-dimensional dense embeddings).
   * Generates contextual embeddings for both student profiles and job listings.
   * Resilient fallback to deterministic dense feature projection if running offline.
3. **Preference Alignment:**
   * Scores alignment between candidate's desired roles, preferred tech hubs, and remote preferences against the opening.

---

### Subsystem 3: FastAPI REST API Endpoints

#### Authentication Routes (`/auth`):
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Register new student, initialize profile, issue access & refresh tokens |
| `POST` | `/auth/login` | Authenticate candidate with email/password and issue fresh JWT |
| `POST` | `/auth/refresh` | Rotate expired access tokens using a valid refresh token |
| `GET` | `/auth/me` | Fetch active user credentials and profile state |

#### Student Profile Routes (`/api/student/profile`):
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/student/profile` | Retrieve verified student master profile |
| `PUT` | `/api/student/profile` | Update profile, trigger completeness score, and re-embed AI vector |
| `GET` | `/api/student/profile/completeness` | Breakdown of section scores, missing items, and optimization tips |

#### Job Feed & Opportunity Routes (`/api/jobs`):
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/jobs/matched-feed` | Paginated candidate-tailored feed ranked by AI Match Score % |
| `GET` | `/api/jobs/{job_id}` | Detailed job listing with personalized match analytics and skill gap |

#### Query Parameters for `/api/jobs/matched-feed`:
* `page`: Page index (default: `1`)
* `limit`: Page size (default: `20`, max: `100`)
* `min_score`: Filter opportunities above a minimum match percentage (e.g. `60.0`)
* `only_eligible`: Strictly return candidates meeting all hard criteria (`true`/`false`)
* `remote_only`: Filter remote opportunities (`true`/`false`)
* `employment_type`: `full_time`, `internship`, `gig`, `contract`
* `city`: Search within specific city hubs (e.g. `Bangalore`, `Pune`)

---

## 3. Directory Layout

```text
leadgen/module_3_backend_and_matching/
├── README.md                       # Comprehensive engine & API documentation
├── config.py                       # JWT secrets, algorithms, scoring weights
├── main.py                         # FastAPI application entrypoint with CORS
├── models/                         # Relational SQLAlchemy 2.0 ORM Models
│   ├── __init__.py
│   ├── user.py                     # Candidate user accounts & roles
│   └── student_profile.py          # Academic, skills, preferences & vector embedding
├── schemas/                        # Pydantic v2 Request/Response Schemas
│   ├── __init__.py
│   ├── auth.py                     # Register, Login, TokenResponse
│   ├── profile.py                  # Profile update, Response, Completeness
│   └── job_feed.py                 # MatchedJobCard, SkillGapReport, FeedResponse
├── auth/                           # Authentication & Session Engine
│   ├── __init__.py
│   ├── security.py                 # Bcrypt password hashing & JWT handlers
│   └── dependencies.py             # OAuth2 Bearer token extractor & get_db
├── matcher/                        # The AI Smart Matching Engine
│   ├── __init__.py
│   ├── embedder.py                 # 384-dimensional vector embedder & cosine similarity
│   ├── rule_filter.py              # Hard eligibility rules & statutory age relief
│   ├── skill_gap_analyzer.py       # Canonical synonyms & missing skills extractor
│   ├── semantic_scorer.py          # Vector similarity computation
│   └── match_orchestrator.py       # Hybrid multi-factor score calculator
├── routes/                         # REST API Route Modules
│   ├── __init__.py
│   ├── auth_routes.py              # Registration, Login, Session
│   ├── profile_routes.py           # Master Profile CRUD & completeness
│   └── feed_routes.py              # Scored & ranked feed queries
└── tests/                          # Full Automated Test Suite (pytest)
    ├── __init__.py
    ├── test_auth.py                # Security & JWT unit tests
    ├── test_matcher.py             # Rule filter, embedder & scoring unit tests
    ├── test_profile.py             # Profile completeness unit tests
    └── test_e2e_api.py             # Full student journey E2E integration test
```

---

## 4. How to Run & Test

### 1. Launch the FastAPI Development Server
```bash
python -m uvicorn module_3_backend_and_matching.main:app --host 0.0.0.0 --port 8000 --reload
```
* **Interactive OpenAPI Swagger Documentation:** Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
* **Alternative ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **System Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

### 2. Run the Test Suite
```bash
# Run Module 3 tests specifically
pytest module_3_backend_and_matching/tests -v

# Run the complete test suite across both Module 2 and Module 3
pytest -v
```

---

## 5. Verification Scorecard

| Test Suite | Focus Area | Test Count | Pass Rate |
| :--- | :--- | :---: | :---: |
| `test_auth.py` | Bcrypt hashing, JWT issuance, token expiration | 4 | **100% Pass** |
| `test_matcher.py` | Rule filter, batch matching, age relaxation, skill gaps | 6 | **100% Pass** |
| `test_profile.py` | Completeness percentage, section scoring | 1 | **100% Pass** |
| `test_e2e_api.py` | End-to-end student registration, profile update, ranked feed | 1 | **100% Pass** |
| **Module 3 Total** | **Full Backend & AI Engine Verification** | **12 / 12** | **100% Pass** |
| **LeadGen Total** | **Combined Module 2 & Module 3 Tests** | **42 / 42** | **100% Pass** |

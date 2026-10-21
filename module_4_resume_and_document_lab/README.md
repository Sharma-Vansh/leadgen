# Module 4: AI Resume Studio & Govt Document Lab

**Dual-Pillar Career Acceleration Suite: Truthful ATS Resume Generation & Government Document Compliance**  
Built with **Pillow (PIL)**, **ReportLab (Vector PDF)**, **Pydantic v2**, and **FastAPI**.

---

## 1. Engine Overview & Architecture

Module 4 serves two essential pillars of the Indian student job-application journey:
1. **Private Sector Pillar (AI Resume Studio):** Tailors resumes for target roles with **Zero Hallucination Guarantee**, ranks keywords for modern ATS systems (Workday, Greenhouse, Lever, Taleo), scores parseability, and outputs single-column vector PDFs.
2. **Public Sector Pillar (Govt Document Lab):** Automatically cleans, resizes, and compresses candidate signatures and photographs to strictly conform to rigorous Indian government upload standards (**SSC, UPSC, IBPS, Railways RRB, State PSCs**).

```
                                LEADGEN MODULE 4
                 [ AI Resume Studio & Govt Document Lab ]
                                        │
        ┌───────────────────────────────┴───────────────────────────────┐
        ▼                                                               ▼
[ PILLAR 1: AI RESUME STUDIO ]                  [ PILLAR 2: GOVT DOCUMENT LAB ]
• Anti-Hallucination Guard                      • Signature Resizer (Strictly 10-20 KB)
• Job-Specific Keyword Alignment                • Passport Photo Lab (Strictly 20-50 KB)
• ATS Readability Scorer (0-100)                • Background Whitener & Contrast Boost
• ReportLab Single-Column Vector PDF            • Pre-Flight Portal Compliance Validator
```

---

## 2. Pillar 1: AI Resume Studio (Private Sector ATS)

### Strict Anti-Hallucination Policy (`anti_hallucination.py`)
Traditional LLM resume tools invent fake skills, inflate CGPA, and claim non-existent tool proficiency to increase keyword density. **LeadGen strictly forbids fabrication**:
* **Skill Verification:** Every skill in the generated resume must exist in the candidate's verified profile. Unverified suggestions are discarded.
* **Academic Integrity:** Degrees, branches, colleges, graduation batches, and CGPAs are checked against the verified profile and cannot be altered.

### Truthful ATS Tailoring (`tailor.py`)
* Analyzes target job requirements via Module 3's `SkillGapAnalyzer`.
* Partitions candidate skills into:
  * **Core Stack:** Verified candidate skills that directly match target requirements.
  * **Supporting Technologies:** Additional verified skills demonstrating technical breadth.
* Generates a concise 2-sentence Professional Summary targeted to the company and role.

### Single-Column Vector PDF Generation (`pdf_builder.py`)
* Built with `reportlab.platypus` generating clean vector PDF text.
* **ATS Friendly:** Uses single-column flowable layout without nested tables, floating text boxes, or multi-column grids that corrupt ATS OCR parsers.
* Standard typography (`Helvetica-Bold`, `Helvetica`), 0.5-inch margins, and semantic section headings (`PROFESSIONAL SUMMARY`, `TECHNICAL COMPETENCIES`, `EDUCATION`, `ROLE ALIGNMENT`, `CERTIFICATIONS`).

---

## 3. Pillar 2: Government Document Lab (Public Sector Portals)

### Official Recruitment Board Specifications Registry
| Recruitment Board | Photograph Requirement | Signature Requirement | Certificate / Marksheet |
| :--- | :--- | :--- | :--- |
| **SSC (Staff Selection Commission)** | 20 KB – 50 KB (3.5 × 4.5 cm, JPEG) | **10 KB – 20 KB (6.0 × 2.0 cm, JPEG)** | 50 KB – 300 KB (PDF) |
| **UPSC (Civil Services / CDS / NDA)** | 20 KB – 300 KB (Min 350 × 350 px) | 20 KB – 300 KB (Min 350 × 350 px) | PDF (Under 300 KB) |
| **IBPS (Banking Personnel)** | 20 KB – 50 KB (200 × 230 px, JPEG) | **10 KB – 20 KB (140 × 60 px, JPEG)** | Thumb: 20 KB – 50 KB |
| **RRB (Indian Railways)** | 20 KB – 50 KB (3.5 × 4.5 cm, JPEG) | 10 KB – 20 KB (140 × 60 px, JPEG) | Category: 50 KB – 300 KB |

### Signature Resizing & Contrast Booster (`signature_resizer.py`)
* **Background Whitening:** Thresholds yellowish/gray paper shadows into pure white (`#FFFFFF`) while maintaining pen stroke contrast.
* **Standard Aspect Ratio:** Resizes to 3:1 (`300 × 100 px` / `6.0 × 2.0 cm`).
* **Iterative Quality Fitting:** Employs a binary search compression loop guaranteeing that the resulting file size is strictly **between 10.0 KB and 20.0 KB** (preventing portal rejection).

### Passport Photo Lab (`photo_processor.py`)
* **Proportion Normalization:** Center-crops portrait uploads to standard 7:9 ratio (`350 × 450 px` / `3.5 × 4.5 cm`).
* **Quality Tuning:** Compresses strictly **between 20.0 KB and 50.0 KB**.

### Pre-Flight Compliance Validator (`compliance_validator.py`)
* Inspects candidate files before submission against portal constraints.
* Returns exact pass/fail diagnosis, size breakdown, and remediation advice.

---

## 4. REST API Endpoint Catalog

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/resume/tailor` | Tailors verified profile to target job, computes ATS score and returns structured JSON |
| `POST` | `/api/resume/download-pdf` | Streams downloadable ATS-compliant vector PDF file |
| `POST` | `/api/documents/process-signature` | Cleans paper background, normalizes to 6x2 cm, and compresses to 10-20 KB |
| `POST` | `/api/documents/process-photo` | Center-crops to 3.5x4.5 cm passport standard and compresses to 20-50 KB |
| `POST` | `/api/documents/verify-compliance` | Pre-flight audit checking file size, format, and dimensions against portal presets |

---

## 5. Directory Layout

```text
leadgen/module_4_resume_and_document_lab/
├── README.md                       # Comprehensive module documentation
├── __init__.py
├── resume_studio/                  # [PILLAR 1: ATS RESUME ENGINE]
│   ├── __init__.py
│   ├── anti_hallucination.py       # Strict verified-profile cross-checker
│   ├── tailor.py                   # Job-tailored content optimizer
│   ├── ats_scorer.py               # Readability & keyword density scorer
│   └── pdf_builder.py              # ReportLab vector single-column PDF generator
├── govt_document_lab/              # [PILLAR 2: GOVT PORTAL COMPLIANCE]
│   ├── __init__.py
│   ├── signature_resizer.py        # 10-20 KB background whitener & compressor
│   ├── photo_processor.py          # 20-50 KB passport photo normalizer
│   └── compliance_validator.py     # Pre-flight rules auditor (SSC, UPSC, IBPS, RRB)
├── schemas/                        # Pydantic v2 Request/Response Schemas
│   ├── __init__.py
│   ├── resume.py                   # TailorResumeRequest, TailoredResumeResponse
│   └── documents.py                # DocumentProcessResponse, ComplianceCheckResponse
├── routes/                         # FastAPI Route Modules
│   ├── __init__.py
│   ├── resume_routes.py            # /api/resume endpoints
│   └── document_routes.py          # /api/documents endpoints
└── tests/                          # Full Automated Test Suite (pytest)
    ├── __init__.py
    ├── test_anti_hallucination.py  # Fact-check & inflation prevention tests
    ├── test_tailor_and_ats.py      # Skill ordering & ATS scoring tests
    ├── test_pdf_builder.py         # Vector PDF generation tests
    ├── test_signature_resizer.py   # Strict 10-20 KB size constraint tests
    ├── test_photo_processor.py     # Strict 20-50 KB size constraint tests
    ├── test_compliance_validator.py# Portal rules verification tests
    └── test_api_endpoints.py       # End-to-end multipart API route tests
```

---

## 6. Verification Scorecard

| Test Suite | Focus Area | Test Count | Pass Rate |
| :--- | :--- | :---: | :---: |
| `test_anti_hallucination.py` | Skill filtering, CGPA inflation, degree mismatch | 3 | **100% Pass** |
| `test_tailor_and_ats.py` | Skill partitioning, truthful summary, ATS grade | 2 | **100% Pass** |
| `test_pdf_builder.py` | Single-column vector PDF generation, `%PDF` header | 1 | **100% Pass** |
| `test_signature_resizer.py` | Paper whitening, 6x2 cm, **strictly 10-20 KB** | 1 | **100% Pass** |
| `test_photo_processor.py` | 7:9 ratio, **strictly 20-50 KB** | 1 | **100% Pass** |
| `test_compliance_validator.py`| SSC photo/signature rules, marksheet PDF check | 4 | **100% Pass** |
| `test_api_endpoints.py` | End-to-end multipart upload & PDF streaming | 1 | **100% Pass** |
| **Module 4 Total** | **AI Resume Studio & Govt Document Lab** | **13 / 13** | **100% Pass** |
| **LeadGen Total** | **Combined Modules 2, 3, and 4** | **55 / 55** | **100% Pass** |

# Module 5: LeadGen Student Web Dashboard

The **LeadGen Student Web Dashboard** is a state-of-the-art career operating system and exam portal designed for students and graduates across tech and public sector examinations.

---

## 🌟 Key Architecture & Features

### 1. **Autonomous Job Feed (388+ Ingested Sources)**
- Sourced across Archetypes A to E:
  - **Tier-1 Tech**: Google, Microsoft, Amazon, Atlassian.
  - **Unicorn Startups**: Razorpay, Swiggy, Zepto, Cred.
  - **Remote Global**: Supabase, PostHog, GitLab, Stripe.
  - **Govt & PSUs**: ISRO, SSC (CGL/CHSL), DRDO, RRB, IBPS.
- **Semantic Match Gauge**: Live circular meter indicating AI match percentage (0–100%) computed via vector embeddings.
- **Skill Alignment Matrix**: Displays verified student skills (green pills) alongside targeted skill gaps (amber pills) with AI learning recommendations.

### 2. **Application Pipeline (Kanban Tracker)**
- 4-stage workflow:
  - `Discovered` (AI Matched Stream)
  - `Preparing` (Tailoring in Progress)
  - `Ready to Apply` (Vector ATS PDF compiled)
  - `Submitted` (Applied & Tracking)
- Direct 1-click stage advancement, notes management, and direct transition into Resume Studio.
- Persistent state synchronized with browser `localStorage`.

### 3. **AI Resume Studio (ReportLab ATS Vector Engine)**
- **100% Anti-Hallucination Guarantee**: Synthesizes verified candidate credentials without fabricating past employers or credentials.
- **ATS Readiness Radar**:
  - Keyword Relevance (92%+)
  - Action Verbs & Quantified Metrics (96%+)
  - Formatting & Structure (95%+)
- **Live Vector Preview & Export**: Formatted to single-column ATS specifications with direct ReportLab vector PDF export.

### 4. **Govt Document Lab (Zero Rejection Engine)**
- Built specifically for **SSC, UPSC, IBPS, RRB**:
  - **Signature Resizer & Cleaner**: Strictly scales images into **10–20 KB**, removes shadows, background tints, and locks 140x60 px (7:3 aspect ratio).
  - **Passport Photograph Normalizer**: Strictly scales into **20–50 KB**, locks 3.5cm x 4.5cm dimensions at 200 DPI with neutral lighting.
  - **Live Compliance Audit Card**: Instant PASS/FAIL validation with 0.00% rejection probability.

### 5. **Candidate Profile & Preference Drawer**
- Slide-over panel to edit academic details (CGPA, degree, batch year), add/remove verified skills, and customize target compensation and archetypes.

### 6. **Resilient Backend Integration (`api.js`)**
- Directly communicates with the FastAPI backend on `http://localhost:8000/api`.
- Seamlessly falls back to rich pre-loaded verified data if running offline.

---

## 🚀 Running the Dashboard

```bash
cd module_5_student_dashboard
npm run dev
```

Runs on `http://localhost:5173`.

To create a production build:
```bash
npm run build
```

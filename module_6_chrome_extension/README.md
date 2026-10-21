# Module 6: Chrome Extension & Autonomous Autofill Assistant

The **LeadGen Chrome Extension** is a Manifest V3 browser assistant that autonomously detects job application forms across all 5 archetypes and autofills candidate credentials in 1 click with guaranteed zero hallucination.

---

## 🌟 Architecture & Capabilities

### 1. **Multi-Platform Form Detection (`form_detector.js`)**
- Identifies ATS and portal forms automatically on page load:
  - **Workday**: Detects `wd-`, `data-automation-id`, and dynamic form models.
  - **Greenhouse**: Detects `#job_application` and `greenhouse.io` URLs.
  - **Lever**: Detects `.application-form` and `jobs.lever.co`.
  - **Ashby & SmartRecruiters**: Scans for standard and custom ATS containers.
  - **Govt Exam Portals (SSC, UPSC, RRB)**: Detects registration number, candidate name, and strict document upload zones.
  - **Generic Applications**: Scans for signals (resume upload, education, experience, phone).

### 2. **Intelligent Field Mapping (`field_mapper.js`)**
- Uses multi-attribute regex heuristics (matching `id`, `name`, `placeholder`, `aria-label`, and surrounding `<label>` text) to classify form inputs into:
  - `firstName`, `lastName`, `fullName`
  - `email`, `phone`
  - `linkedin`, `github`, `portfolio`
  - `university`, `degree`, `major`, `cgpa`, `graduationYear`
  - `address`, `city`, `state`, `postalCode`, `country`
  - `summary`, `coverLetter`, `gender`, `dob`
- Dispatches synthetic events (`input`, `change`, `blur`) ensuring modern reactive frameworks (React, Angular, Workday) correctly ingest the filled values.
- Adds visually prominent glowing blue borders (`.leadgen-filled-field`) to filled fields so candidates can inspect before submission.

### 3. **In-Page Floating Widget (`autofill_engine.js`)**
- Appears unobtrusively in the bottom-right corner when an application form is detected.
- Displays target company, platform badge, and a prominent **"⚡ Autofill Application (1-Click)"** button.
- Flags compliance for Govt exam portals if 10–20 KB signatures or 20–50 KB photos are required.

### 4. **Extension Popup Dashboard (`popup/`)**
- Sleek dark theme matching Module 5's design system.
- Displays active tab detection status in real time.
- 1-Click "Copy Cover Letter" tool.
- 1-Click "Open Web Dashboard" link to launch the student dashboard (`http://localhost:5173`).
- Verified compliance status for SSC/UPSC photos and signatures.

### 5. **Background Service Worker (`background/service_worker.js`)**
- Manages storage synchronization between local browser storage (`chrome.storage.local`) and the LeadGen FastAPI backend (`http://localhost:8000/api/profile/me`).

---

## 🚀 How to Install & Use in Google Chrome / Brave / Edge

1. Open your browser and navigate to:
   ```
   chrome://extensions/
   ```
2. Enable **Developer mode** (toggle in the top-right corner).
3. Click the **Load unpacked** button.
4. Select the directory:
   ```
   c:\Users\ASUS\.gemini\antigravity-ide\scratch\leadgen\module_6_chrome_extension
   ```
5. The **LeadGen AI — Autonomous Job & Exam Autofill** extension is now active!
6. Navigate to any job application page (e.g. Greenhouse, Workday, Lever, or SSC) to see the 1-click autofill widget in action.

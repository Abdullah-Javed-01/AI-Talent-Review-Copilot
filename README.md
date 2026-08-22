# Talent Review Copilot

An evidence-first recruitment review prototype for high-volume internship hiring.

The system combines application-form data with resume/CV evidence, applies a deterministic role-specific rubric, separates technical evidence from operational fit, and gives recruiters a review queue where the final decision always remains human.

> Independent prototype inspired by a public high-volume internship hiring use case. This is not an official Alphabridge product.

## What problem it solves

High-volume internship hiring creates a review bottleneck: recruiters may receive thousands of applications, while the useful evidence needed to compare candidates is scattered across form responses and CVs.

Talent Review Copilot turns that intake into a structured review workflow:

```text
Application Form / Sheet
        +
Candidate Resume / CV
        ↓
Form normalization
        ↓
Resume PDF parsing
        ↓
Role-specific evidence extraction
        ↓
Deterministic rubric scoring
        +
Operational-fit checks
        ↓
Recruiter review queue
        ↓
Shortlist / Hold / Not Selected
```

The system does **not** make hiring decisions. It organizes evidence and prioritizes review; the recruiter decides what happens next.

## Supported internship tracks

The current MVP supports four technical tracks with separate 22-point rubrics:

| Track | Example evidence considered |
|---|---|
| ML/AI | Python, ML fundamentals, project depth, data handling, evaluation, ML libraries, Git/GitHub, practical exposure |
| Data Science | Python, statistics/EDA, SQL, ML fundamentals, data handling, visualization, evaluation, practical exposure |
| Data Engineering | Python/SQL, ETL and pipelines, databases, data modeling, warehouse/cloud exposure, Git/GitHub, projects |
| DevOps | Linux/scripting, Git/GitHub, containers, CI/CD, cloud, networking, monitoring/deployment, projects |

The rubric layer is configurable, so additional roles can be added without replacing the ingestion or recruiter-review workflow.

## Evidence philosophy

The prototype separates **mentioned** skills from **demonstrated** evidence.

A technology appearing only in a skills or certification list should not be treated the same as contextual proof such as:

> Built a Python ETL pipeline that ingested CSV and API data into PostgreSQL.

The current extractor excludes skills and certification sections from strong contextual evidence snippets. Those sections can still contribute as mentions, but demonstrated evidence is expected to come from project, experience, research, or other contextual resume content.

## What comes from the form vs. the CV

| Information | Source |
|---|---|
| Name, email, phone | Application form |
| University, semester | Application form |
| Applied role | Application form |
| Current city / Lahore address | Application form |
| Shift availability | Application form |
| Onsite availability | Application form |
| LinkedIn URL | Application form |
| Skills, tools, projects | Resume/CV |
| ML / data / DevOps evidence | Resume/CV |
| Supporting evidence snippets | Resume/CV |
| Evidence score | Deterministic role rubric |
| Review priority | Deterministic role rubric |
| Operational status | Form-derived rule check |
| Shortlist / Hold / Not Selected | Human recruiter |

The dashboard shows these sources explicitly so recruiters can see where each conclusion came from.

## Recruiter-facing data intake

The Streamlit app includes a **Data Intake** page so a recruiter does not need to open the codebase or run preprocessing scripts manually.

The current intake workflow supports:

1. Uploading a Google Forms / Google Sheets export (`.csv` or `.xlsx`)
2. Normalizing common form-question wording into the internal schema
3. Uploading multiple candidate PDF CVs
4. Matching uploaded CVs to applicants
5. Processing the applications into candidate profiles
6. Opening the review dashboard

`.xlsx` is preferred when available because it can preserve a Google Drive file hyperlink from a form-upload response when that hyperlink is present in the sheet export.

### Google Drive note

The prototype does **not** bypass Google permissions. A Drive URL is kept as provenance, but the CV is not treated as parsed until the actual PDF is available.

A production integration would use Google OAuth so an authorized recruiter can connect the response Sheet and Form-upload folder and let the app retrieve CVs directly from Drive.

## Recruiter dashboard

The review dashboard provides:

- Candidate search
- Role filtering
- Technical-priority filtering
- Operational-status filtering
- Recruiter-decision filtering
- Minimum evidence-score filtering
- Review queue export
- Candidate profile view
- Application-form provenance
- Role-specific score breakdown
- Exact supporting resume snippets
- Operational-fit summary
- Shortlist / Hold / Not Selected actions
- Shortlist export
- Manual-review fallback when a CV is missing or cannot be parsed

The header automatically distinguishes between **synthetic demo data**, **imported applicant data**, and a **mixed** workspace.

## Review priorities

For the current MVP, the technical score thresholds are:

```text
17–22  → Priority Review
11–16  → Good Potential
 6–10  → Developing Profile
 0–5   → Insufficient Evidence
```

These thresholds are configurable product assumptions, not universal hiring standards.

Operational fit is intentionally separate from technical evidence:

- `READY` — Lahore-based and available for onsite work and the required shift
- `CONFIRM_LOCATION` — outside Lahore but indicated onsite availability
- `REQUIREMENT_MISMATCH` — onsite or required-shift availability is not met
- `MANUAL_REVIEW` — the profile cannot be processed reliably

## Demo dataset

The public repository ships with **30 synthetic candidates** across:

- ML/AI
- Data Science
- Data Engineering
- DevOps

The dataset intentionally includes strong, moderate, developing, weak, location-check, requirement-mismatch, and manual-review cases.

`DEMO-030` intentionally has no resume file so the manual-review fallback can be demonstrated.

No real applicant information is included in the public demo data.

## Private real-world validation

The intake-to-review flow was also tested privately with a recruiter-style Google Form / Google Sheets export and an actual CV. That validation exercised:

```text
Form submission
→ XLSX export
→ form-field normalization
→ Drive-link provenance
→ actual PDF upload
→ resume parsing
→ evidence extraction
→ ML/AI rubric scoring
→ recruiter dashboard
```

The real validation files are intentionally excluded from the public repository.

## Architecture

```text
app/
├── dashboard.py          # Recruiter review dashboard
├── form_importer.py      # Form/Sheet export normalization
├── validator.py          # Input validation
├── resume_parser.py      # PDF parsing with pypdf
├── evidence_extractor.py # ML/AI evidence extraction
├── role_evidence.py      # Non-ML role evidence extraction
├── score_engine.py       # ML/AI deterministic rubric
├── role_score_engine.py  # Role-aware scoring layer
├── role_rubrics.py       # Rubric definitions
├── decision_store.py     # Local recruiter decision persistence
├── build_profiles.py     # End-to-end profile builder
└── pages/
    └── 1_Data_Intake.py  # Recruiter-facing intake page

scripts/
└── generate_demo_dataset.py

data/
├── applications/
├── processed/
└── resumes/
```

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/Abdullah-Javed-01/AI-Talent-Review-Copilot.git
cd AI-Talent-Review-Copilot
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the dashboard

```powershell
streamlit run app\dashboard.py
```

The app will open locally at the URL shown by Streamlit.

## Regenerate the synthetic demo

```powershell
python scripts\generate_demo_dataset.py
python app\build_profiles.py
```

This recreates the synthetic application CSV, synthetic PDF resumes, and processed candidate profiles.

## Import a form export from the command line

The recruiter-facing Data Intake page is the preferred workflow, but the importer can also be run directly:

```powershell
python app\form_importer.py "applications_export.xlsx"
```

Then build profiles:

```powershell
python app\build_profiles.py --applications data\applications\imported_applications.csv
```

## Privacy and responsible-use design

This project is designed as a recruiter-assistance tool, not an autonomous hiring system.

Current safeguards include:

- Human recruiter remains the final decision-maker
- Technical evidence and operational fit are shown separately
- Missing/unreadable resumes go to manual review
- Exact supporting resume excerpts are shown for auditability
- Skills/certification lists are excluded from strong demonstrated evidence
- Real imported form/CV data is ignored by Git
- Recruiter decision storage is local and ignored by Git
- Gender is not used in ranking
- No protected-attribute inference is used for scoring

Any production deployment should add authentication, role-based access control, encrypted storage, retention/deletion policies, audit logging, secure file handling, and a formal review of applicable employment/privacy requirements.

## Current limitations

- Resume extraction is rule-based/deterministic rather than LLM-based
- PDF parsing depends on extractable text; scanned-image CVs are not the primary supported path
- Google Drive retrieval is not automated yet
- Recruiter decisions are stored locally in the prototype
- The current rubric is an MVP and should be calibrated with the employer's actual hiring criteria
- This prototype has not been benchmarked at 10,000+ real applicants

## Possible next steps

- Google OAuth + direct Google Sheets/Drive intake
- Persistent database for candidates and recruiter decisions
- Recruiter authentication and permissions
- Configurable rubric editor
- More internship tracks
- Structured evaluation set for rubric calibration
- LLM-assisted evidence extraction while keeping deterministic scoring and human review
- Applicant lifecycle tracking from application → interview → internship → full-time review

## Tech stack

- Python
- Streamlit
- Pandas
- Pydantic
- pypdf
- ReportLab
- openpyxl

## Status

**MVP complete for public demonstration.**

The current release demonstrates multi-role high-volume candidate review, recruiter-facing intake, resume evidence extraction, deterministic scoring, operational checks, provenance, manual-review fallback, and human decision controls.

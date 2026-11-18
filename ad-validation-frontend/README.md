# AD Validation & Reconciliation Tool

## Executive summary

This solution provides a structured, business-rule-driven validation workflow for comparing Active Directory and Azure identity data. It allows users to upload source files, apply a consistent set of validation checks, and review operational issues in a clear, stakeholder-friendly dashboard.

The platform is intentionally designed as a modular full-stack application with a responsive Angular frontend and a Python FastAPI backend. This separation keeps the user experience lightweight while preserving clear ownership of business logic, data processing, and validation rules.

## Solution overview

The application is composed of two core layers:

- Frontend: Angular 18 single-page application in [src](src)
- Backend: FastAPI service in [backend](backend)

The end-to-end workflow is straightforward: users upload source files, the backend validates the data against business rules, and the frontend presents the results in a structured dashboard for review and export.

---

## Technology stack

### Frontend

- Angular 18
- Angular Material
- TypeScript
- RxJS
- XLSX export support

### Backend

- Python
- FastAPI
- Pandas
- OpenPyXL
- Pytest

### Local integration

- Angular development server with proxy support
- FastAPI service running on localhost:8000

---

## What the app does

The tool lets a user upload three files:

- On-prem AD dump
- Azure AD dump
- Vendor and employee list

It then validates the data against business rules such as:

- 11-data-center checks
- name mismatch detection
- disabled-but-active accounts
- accounts with stale logins
- accounts missing from Azure

The result is displayed in a tabbed report with summary cards, search, pagination, and export options.

---

## Folder structure

```text
ad-validation-frontend/
├── angular.json
├── package.json
├── package-lock.json
├── proxy.conf.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.spec.json
├── README.md
├── ARCHITECTURE.md
├── BACKEND.md
├── public/
│   └── favicon.ico
├── src/
│   ├── app/
│   │   ├── app.component.ts
│   │   ├── app.config.ts
│   │   ├── app.routes.ts
│   │   ├── models.ts
│   │   ├── validation.service.ts
│   │   ├── shell/
│   │   ├── upload-box/
│   │   ├── validation-page/
│   │   ├── summary-cards/
│   │   ├── result-table/
│   │   └── configure-columns-dialog/
│   ├── index.html
│   ├── main.ts
│   └── styles.css
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── reader.py
│   │   ├── settings.py
│   │   └── checks/
│   │       ├── __init__.py
│   │       ├── dc_count.py
│   │       ├── name_match.py
│   │       ├── inactive.py
│   │       ├── last_login.py
│   │       └── in_azure.py
│   ├── scripts/
│   │   └── make_sample_data.py
│   ├── tests/
│   │   ├── test_health.py
│   │   └── test_reader.py
│   ├── requirements.txt
│   └── .venv/
├── dist/
│   └── build output
├── node_modules/
└── .angular/
```

---

## Quick start

### Frontend

```bash
npm install
npm start
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Documentation

- [README.md](README.md): high-level overview, purpose, setup, and quick reference
- [ARCHITECTURE.md](ARCHITECTURE.md): technical architecture, processing flow, and implementation detail
- [BACKEND.md](BACKEND.md): backend-specific design, request flow, rules, and validation logic

---

## Project purpose

The tool supports review of identity and access data across source systems, with validation rules for:

- data center consistency
- account name mismatches
- stale or inactive records
- missing Azure coverage

The final output is a report with summary metrics and issue details suitable for operational review.

For detailed technical design, validation flow, file-by-file implementation notes, and architecture references, see [ARCHITECTURE.md](ARCHITECTURE.md).

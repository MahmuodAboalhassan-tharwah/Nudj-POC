# Nudj (نُضْج) — HR Maturity Assessment Platform

## Product Overview

Nudj is a multi-tenant SaaS platform that digitizes Tharwah Holding Company's proprietary 9-domain HR Maturity Assessment Framework. It replaces manual Excel-based workflows with a scalable, Arabic-first bilingual platform.

**Owner:** Tharwah Holding Company (Tadawul: 9606.SR)
**Market:** Saudi Arabia (Vision 2030 alignment)
**Codename:** Nudj (نُضْج — Arabic for "maturity")

## Business Goals

| Metric | Baseline | Target |
|--------|----------|--------|
| Assessment cycle time | 4-6 weeks | < 2 weeks |
| Concurrent assessments | 3-5 | 15+ |
| Platform MAU | 0 | 200+ |
| ARR | SAR 0 | SAR 2M+ |
| AI Coach engagement | N/A | 40%+ |

## User Roles (4 hierarchical)

| Role | Scope | Key Actions |
|------|-------|-------------|
| **Super Admin** | All orgs | Create assessments, manage framework, generate reports, access BDW, admin AI Coach |
| **Analyst** | Assigned orgs | Review evidence, validate scores, generate reports, use AI Coach |
| **Client Admin** | Own org | Coordinate assessment, invite assessors, view results, use AI Coach |
| **Assessor** | Assigned domains | Complete maturity selections, upload evidence, use AI Coach for own domains |

## HR Maturity Framework

### 9 Domains with Weights
1. Organizational Development — 12%
2. Performance Management — 15%
3. Total Rewards — 12%
4. HR Operations — 8%
5. Career Path Planning — 10%
6. Succession Planning — 10%
7. Workforce Planning — 10%
8. Talent Acquisition — 12%
9. Talent Development — 15%

### 3 Evaluation Dimensions
- Existence & Progress — 30%
- Application — 50%
- Automation — 20%

### 4 Maturity Levels
| Level | English | Arabic | Score Mapping |
|-------|---------|--------|--------------|
| 1 | Foundation | التأسيس | 0% |
| 2 | Partial Development | التطوير الجزئي | 33% |
| 3 | Integration | التكامل | 67% |
| 4 | Excellence | التميز والتحسين المستمر | 100% |

### Scoring Formula
```
Element Score = Maturity Level mapped to percentage (0%, 33%, 67%, 100%)
Dimension Score = Weighted average of element scores
Domain Score = (Existence × 0.30) + (Application × 0.50) + (Automation × 0.20)
Overall Score = Σ(Domain Score × Domain Weight)
```

## Tech Stack

### Frontend
- **Framework:** React 19 with TypeScript (strict mode)
- **Build/SSR:** Vite 6 with SSR enabled (server-side rendering)
- **State Management:** Zustand (lightweight) or TanStack Query (server state)
- **Routing:** React Router 7 (with SSR data loaders)
- **Styling:** TailwindCSS 4
- **i18n:** react-i18next (Arabic + English, RTL support)
- **Charts:** Recharts or ApexCharts (RTL-compatible)
- **Forms:** React Hook Form + Zod validation
- **Testing:** Vitest + React Testing Library
- **Linting:** ESLint + Prettier

### Backend
- **Framework:** FastAPI 0.115+ (async Python)
- **Auth:** JWT via python-jose + passlib (bcrypt)
- **Database:** PostgreSQL (JSONB for flexible score storage)
- **ORM:** SQLAlchemy 2.0 (async) + Alembic migrations
- **Cache:** Redis 6.4 via aioredis
- **Task Queue:** Celery 5.5 + celery-beat (or ARQ for async)
- **Real-time:** FastAPI WebSockets
- **Message Queue:** Kafka (confluent-kafka / aiokafka)
- **AI/ML:** LangChain + LLM API (Claude or GPT)
- **API Docs:** Auto-generated OpenAPI/Swagger (built into FastAPI)
- **Validation:** Pydantic v2 (built into FastAPI)
- **Code Quality:** Ruff (linter + formatter), mypy (type checking)
- **Python:** 3.12+

### Infrastructure
- **Container:** Docker + docker-compose
- **Data Residency:** Saudi Arabia (mandatory — PDPL/NCA ECC)
- **CDN:** For static assets
- **Object Storage:** S3/Azure Blob for evidence files

## Feature Modules

### V1 (Core Platform)
- **Authentication & Authorization** — Invitation-based registration, RBAC (4 roles), SSO (Azure AD, Google), MFA, JWT
- **Assessment Management** — Project creation, questionnaire interface (Arabic maturity descriptions), evidence upload (74+ checklist items), automated scoring engine, workflow states (Draft → In Progress → Under Review → Revision Requested → Completed → Archived)
- **Dashboards** — Tharwah Portfolio Dashboard (all clients), Client Organization Dashboard (single org), Assessment Progress Tracker
- **Reporting** — Maturity Assessment Report (PDF), Ad-Hoc Comparative Report (internal)
- **Notifications** — Email (SendGrid/SES) + In-App notification center
- **Administration** — Organization management (ISIC sector codes, size bands, regions), Framework configuration (weights), User management, Audit trail (5-year retention)
- **Collaboration** — Comments & discussion (threaded, @mentions), Assessment delegation

### V2 (Intelligence Layer)
- **Benchmark Data Warehouse (BDW)** — Anonymized assessment data, ETL pipeline (24h SLA), 19-field record model, org_cohort_id for longitudinal tracking
- **Benchmark Comparison Reports** — Client vs. peer cohort (sector/size/region), minimum cohort size of 5
- **Longitudinal Progress Reports** — Multi-assessment trajectory tracking
- **Industry Insights Data Engine** — Query builder for aggregate analytics, Super Admin only
- **Pre-Built Industry Report Templates** — 6 template types (Kingdom Overview, Sector Deep Dive, etc.)
- **AI HR Maturity Coach** — RAG-based conversational agent, domain-specific guidance, improvement plan generator, knowledge base management, interaction analytics, guardrails & safety

## Key Non-Functional Requirements

- **Performance:** Page loads < 2s, API < 500ms, Dashboard < 3s, AI Coach < 5s
- **Security:** AES-256 at rest, TLS 1.2+ in transit, OWASP Top 10, tenant isolation, PDPL + NCA ECC
- **Scalability:** 500 orgs, 5000 users, 2000 concurrent, 50K evidence files, 10K+ BDW records
- **i18n:** Arabic-first with full RTL, bilingual toggle, Hijri date option, Saudi locale
- **Data:** 7-year assessment retention, 5-year evidence retention, 2-year AI Coach logs

## Anonymization Rules (BDW)

- Minimum cohort size: 5 organizations
- PII stripped at ETL boundary
- Benchmark outputs rounded to integer
- Outlier suppression (min/max from single org → show median + IQR)
- Consent flag required per organization

## Project Directory Structure

```
POC/
├── .claude/
│   ├── agents/               # Agent definitions (pipeline)
│   │   ├── requirements-analyst.md
│   │   ├── task-splitter.md
│   │   ├── coder.md
│   │   ├── code-reviewer.md
│   │   └── security-reviewer.md
│   └── settings.local.json
├── pipeline/                  # Inter-agent artifacts
│   ├── requirements/          # Output from requirements-analyst
│   ├── tasks/                 # Output from task-splitter + coder results
│   └── reviews/               # Output from code-reviewer + security-reviewer
├── PROJECT_CONTEXT.md         # This file
├── CLAUDE.md                  # Coding conventions
├── PRD_Nudj_HR_Maturity_Platform_v2.0.docx
├── PRD_Tharwah_HR_Maturity_Assessment_Platform_v1.0 1.docx
├── docs/                      # Reference documents (journey maps, etc.)
└── src/                       # Source code (created during development)
    ├── frontend/              # React + Vite SSR application
    └── backend/               # FastAPI application
```

## User Journeys (4 Personas × 6 Stages = 24 Total)

Full journey map: `docs/USER_JOURNEY_MAP_v2.md`

### Journey Summary by Persona

| Persona | Stages | Key Flow |
|---------|--------|----------|
| **Noura (Client Admin)** | Invitation → Setup & Team Invite → Monitor Progress → Submit for Review → View Results → Benchmark Comparison (V2) |
| **Ahmed (Assessor)** | Onboarding → Assessment → Evidence Upload → Review & Revise → Results View → Ask AI Coach (V2) |
| **Salma (Analyst)** | Assignment → Monitoring → Evidence Review → Scoring & Report → Benchmark Generation (V2) → AI Coach for Advisory (V2) |
| **Fahad (Super Admin)** | Client Onboarding → Portfolio Oversight → Quality Assurance → Benchmark & Industry Reporting (V2) → AI Coach Administration (V2) |

### Critical Pain Points (UX Priority)

1. **Evidence Upload (Highest Friction)** — Assessors struggle to find, gather, and upload documents. Needs: drag-and-drop, mobile upload, example descriptions, clear checklists.
2. **Progress Tracking** — Client Admins anxious about team completion. Needs: real-time dashboards, per-assessor status, automated reminders.
3. **Team Coordination** — Getting department heads to complete on time. Needs: auto-reminders, easy delegation, time estimates per domain.
4. **Review Pressure** — Analysts validating claims against evidence. Needs: private notes, evidence status indicators, efficient review workflows.
5. **Onboarding Reluctance** — Assessors see it as "another task." Needs: seamless registration, time estimates, Arabic walkthrough, mobile-first design.

### V2 Value Loop
```
Complete Assessment → See Benchmark vs Peers → Ask AI Coach for Improvements
        ↑                                                          ↓
        └──────── Re-Assess to Track Progress ←── Implement Changes
```

### Key Metrics
- **46+ Design Opportunities** mapped to PRD requirements (REQ-*)
- **Peak Positive Moment:** Benchmark comparison + AI Coach actionable plans
- **All 4 personas** interact with AI Coach (each with different use case)

## PRD References

- **V1.0:** `PRD_Tharwah_HR_Maturity_Assessment_Platform_v1.0 1.docx` — Core platform requirements
- **V2.0:** `PRD_Nudj_HR_Maturity_Platform_v2.0.docx` — Adds BDW, Industry Reporting, AI Coach
- **User Journey Map:** `docs/USER_JOURNEY_MAP_v2.md` — 4 persona journeys with pain points and opportunities

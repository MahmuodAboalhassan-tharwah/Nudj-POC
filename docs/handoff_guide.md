# Nudj Platform Handoff Guide

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Architecture Map](#3-architecture-map)
4. [Module Inventory](#4-module-inventory)
5. [Development Philosophy](#5-development-philosophy)
6. [Getting Started](#6-getting-started)
7. [Key Documentation References](#7-key-documentation-references)
8. [Multi-Agent Pipeline](#8-multi-agent-pipeline)

---

## 1. Project Overview

### What is Nudj?

**Nudj (نُضْج)** is an Arabic-first, bilingual SaaS platform for HR Maturity Assessment built for the Saudi Arabian market. It digitizes Tharwah Holding Company's proprietary 9-domain HR framework, replacing manual Excel-based workflows with an automated, scalable platform.

**Owner:** Tharwah Holding Company (Tadawul: 9606.SR)
**Market:** Saudi Arabia (Vision 2030 alignment)
**Compliance:** PDPL (Personal Data Protection Law) + NCA ECC (National Cybersecurity Authority Essential Controls)

### Core Capabilities

- **9 HR Domains** with configurable weights (Organizational Development, Performance Management, Total Rewards, HR Operations, Career Path Planning, Succession Planning, Workforce Planning, Talent Acquisition, Talent Development)
- **3 Evaluation Dimensions** per domain: Existence (30%), Application (50%), Automation (20%)
- **4 Maturity Levels**: Foundation (0%), Partial Development (33%), Integration (67%), Excellence (100%)
- **Multi-tenant architecture** with organization-level data isolation
- **4 User Roles**: Super Admin, Analyst, Client Admin, Assessor
- **Bilingual UI**: Arabic (primary) + English with full RTL support

### Business Goals

| Metric | Baseline | Target |
|--------|----------|--------|
| Assessment cycle time | 4-6 weeks | < 2 weeks |
| Concurrent assessments | 3-5 | 15+ |
| Platform MAU | 0 | 200+ |
| ARR | SAR 0 | SAR 2M+ |

### Product Versions

- **V1 (Core Platform)**: Authentication, Assessment Management, Dashboards, Reporting, Notifications, Administration, Collaboration
- **V2 (Intelligence Layer)**: Benchmark Data Warehouse (BDW), Benchmark Comparison Reports, Longitudinal Progress Reports, Industry Insights Engine, AI HR Maturity Coach (RAG-based)

---

## 2. Tech Stack

### Frontend

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | React | 19.0.0 | UI library |
| **Language** | TypeScript | 5.7.2 | Type safety (strict mode) |
| **Build Tool** | Vite | 6.0.11 | Fast dev server + HMR |
| **Routing** | React Router | 7.1.1 | Client-side routing |
| **State Management** | Zustand | 5.0.2 | Lightweight global state |
| **Server State** | TanStack Query | 5.62.11 | Data fetching + caching |
| **Styling** | TailwindCSS | 4.0.0-beta.8 | Utility-first CSS |
| **UI Components** | shadcn/ui | 3.8.4 | Radix UI + Tailwind |
| **Forms** | React Hook Form | 7.71.1 | Form state management |
| **Validation** | Zod | 3.25.76 | Schema validation |
| **i18n** | react-i18next | 15.2.0 | Bilingual (ar/en) |
| **HTTP Client** | Axios | 1.7.9 | API requests |
| **Testing** | Vitest + React Testing Library | 4.0.18 | Unit/integration tests |

### Backend

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | FastAPI 0.109+ | Async Python web framework |
| **Language** | Python | 3.12+ (required) |
| **ORM** | SQLAlchemy 2.0 | Async database access |
| **Validation** | Pydantic v2 | Request/response schemas |
| **Migrations** | Alembic 1.13+ | Database versioning |
| **Database** | PostgreSQL | Relational data + JSONB |
| **Cache** | Redis 5.0+ | Session/cache storage |
| **Auth** | python-jose + argon2 | JWT + password hashing |
| **MFA** | pyotp | TOTP 2FA |
| **Task Queue** | Celery 5.5+ | Background jobs |
| **Message Queue** | Kafka | Event streaming (V2) |
| **AI/ML** | LangChain | RAG for AI Coach (V2) |
| **Reporting** | WeasyPrint + Jinja2 | PDF generation |
| **Testing** | pytest + httpx | Async test framework |

### Infrastructure

- **Container:** Docker + docker-compose (local dev)
- **Data Residency:** Saudi Arabia (PDPL mandatory)
- **Object Storage:** S3/Azure Blob for evidence files
- **CDN:** Static asset delivery

---

## 3. Architecture Map

### Frontend Structure

```
src/frontend/
├── index.html
├── vite.config.ts              # Vite configuration
├── package.json                # Dependencies
├── src/
│   ├── main.tsx                # Entry point
│   ├── app.tsx                 # Root component + providers
│   ├── router.tsx              # Route definitions
│   ├── features/
│   │   ├── auth/               # Authentication feature
│   │   │   ├── pages/          # Smart components (route targets)
│   │   │   ├── components/     # Presentational components
│   │   │   ├── api/            # API calls + TanStack Query hooks
│   │   │   ├── store/          # Zustand slices (if needed)
│   │   │   └── types/          # TypeScript interfaces
│   │   ├── assessments/        # Core assessment feature
│   │   ├── organizations/      # Organization management
│   │   ├── dashboards/         # Analytics dashboards
│   │   ├── admin/              # Super Admin console
│   │   ├── comments/           # Collaboration/commenting
│   │   └── notifications/      # Notification center
│   ├── shared/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ui/             # shadcn/ui components
│   │   │   └── layout/         # Layout components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utilities (api client, auth)
│   │   └── types/              # Shared TypeScript types
│   ├── i18n/
│   │   ├── ar.json             # Arabic translations
│   │   └── en.json             # English translations
│   └── styles/
│       └── globals.css         # Tailwind + global styles
└── tests/
    └── <feature>/              # Tests mirror src/ structure
```

### Backend Structure

```
src/backend/
├── main.py                     # FastAPI app factory + middleware
├── config.py                   # Settings (pydantic-settings)
├── database.py                 # SQLAlchemy async engine + session
├── dependencies.py             # Shared FastAPI dependencies
├── requirements.txt            # Python dependencies
├── alembic/                    # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/               # Migration files
│       ├── 001_create_auth_tables.py
│       ├── 002_create_audit_log_table.py
│       ├── 003_create_assessment_tables.py
│       ├── 004_create_organization_table.py
│       ├── 005_create_notification_tables.py
│       ├── 006_create_comments_table.py
│       ├── 007_create_delegations_table.py
│       └── 008_create_framework_config_table.py
├── app/
│   ├── auth/                   # Authentication & authorization
│   │   ├── router.py           # FastAPI endpoints
│   │   ├── schemas.py          # Pydantic request/response models
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   ├── service.py          # Business logic
│   │   ├── dependencies.py     # Auth dependencies
│   │   └── exceptions.py       # Custom exceptions
│   ├── assessments/            # Core assessment engine
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── scoring.py          # Scoring formula
│   │   └── exceptions.py
│   ├── organizations/          # Multi-tenant management
│   ├── framework/              # Domain/dimension config
│   ├── dashboards/             # Analytics aggregation
│   ├── reports/                # PDF generation
│   ├── notifications/          # Email + in-app
│   ├── comments/               # Collaboration
│   ├── delegations/            # Task assignment
│   ├── admin/                  # Admin operations
│   └── common/
│       ├── models.py           # Base models (TimestampMixin, etc.)
│       ├── schemas.py          # Shared schemas (pagination, errors)
│       ├── exceptions.py       # Base exceptions + handlers
│       ├── middleware.py       # Tenant isolation, logging
│       └── utils.py            # Helper functions
├── tasks/                      # Celery background tasks
│   ├── celery_app.py
│   ├── email_tasks.py
│   └── etl_tasks.py            # BDW ETL (V2)
└── tests/
    ├── conftest.py             # Fixtures (async db, test client)
    └── <module>/
        ├── test_router.py
        ├── test_service.py
        └── test_models.py
```

### Scoring Formula

```python
# Element Score
element_score = maturity_level_mapping[selected_level]  # 0%, 33%, 67%, 100%

# Dimension Score (per domain)
dimension_score = weighted_average(element_scores)

# Domain Score
domain_score = (
    (existence_score * 0.30) +
    (application_score * 0.50) +
    (automation_score * 0.20)
)

# Overall Score
overall_score = sum(domain_score * domain_weight for each domain)
```

---

## 4. Module Inventory

### Backend Modules (10)

| Module | Status | Purpose | Key Files |
|--------|--------|---------|-----------|
| **auth** | Complete | User authentication, RBAC, JWT, MFA | `models.py`, `service.py`, `dependencies.py` |
| **organizations** | Complete | Multi-tenant organization management | `models.py`, `service.py` |
| **assessments** | Complete | Core assessment engine, scoring | `models.py`, `service.py`, `scoring.py` |
| **framework** | Complete | Domain/dimension weight configuration | `models.py`, `service.py` |
| **dashboards** | Complete | Analytics aggregation, KPIs | `router.py`, `service.py` |
| **reports** | Complete | PDF generation (maturity reports) | `router.py`, `service.py` |
| **notifications** | Complete | Email + in-app notifications | `models.py`, `service.py` |
| **comments** | Complete | Threaded discussions, @mentions | `models.py`, `service.py` |
| **delegations** | Complete | Assessment task delegation | `models.py`, `service.py` |
| **admin** | Complete | User/org admin console | `router.py`, `service.py` |
| **common** | Complete | Shared models, exceptions, middleware | `models.py`, `middleware.py` |

### Frontend Features (7)

| Feature | Status | Purpose | Key Pages/Components |
|---------|--------|---------|---------------------|
| **auth** | Complete | Login, register, MFA | `LoginPage`, `RegisterPage`, `MFASetupPage` |
| **admin** | Complete | Super Admin console | `UsersPage`, `OrganizationsPage`, `FrameworkConfigPage` |
| **assessments** | Complete | Assessment questionnaire + evidence | `AssessmentDetailPage`, `AssessmentListPage` |
| **organizations** | Complete | Organization profile | `OrganizationDetailPage` |
| **dashboards** | Complete | Analytics charts | `DashboardPage`, `ProgressTracker` |
| **comments** | Complete | Discussion threads | `CommentList`, `CommentForm` |
| **notifications** | Complete | Notification center | `NotificationCenter`, `NotificationBell` |

### Database Migrations (8)

1. `001_create_auth_tables.py` — Users, roles, permissions, sessions
2. `002_create_audit_log_table.py` — Audit trail (5-year retention)
3. `003_create_assessment_tables.py` — Assessments, domains, element responses
4. `004_create_organization_table.py` — Organizations, sectors, regions
5. `005_create_notification_tables.py` — Notifications, preferences
6. `006_create_comments_table.py` — Threaded comments
7. `007_create_delegations_table.py` — Assessment task delegations
8. `008_create_framework_config_table.py` — Domain/dimension weights

---

## 5. Development Philosophy

### Core Principles

1. **Arabic-first bilingual UI** — Every user-facing string must exist in both `ar.json` and `en.json`
2. **Role-Based Access Control (RBAC)** — 4 roles with strict hierarchical permissions
3. **Tenant isolation** — Every query filters by `organization_id` (enforced via middleware)
4. **PDPL compliance** — Encryption at rest (AES-256), in transit (TLS 1.2+), audit logs, deletion requests
5. **Security-first** — OWASP Top 10 protections, NCA ECC standards, no hardcoded secrets
6. **Test coverage** — Every component needs tests (`.test.tsx` or `test_*.py`)

### Coding Conventions

#### React (Frontend)

```tsx
// Named exports only — no default exports
export function AssessmentCard({ score, domain, onSelect }: AssessmentCardProps) {
  // ...
}

// Props interface colocated with component
interface AssessmentCardProps {
  score: number;
  domain: string;
  onSelect: (domainId: string) => void;
}
```

**Rules:**
- **Named exports** only — no `export default`
- **Function components** only — no class components
- **TypeScript strict** — no `any`, explicit return types on public APIs
- **Props interfaces** — suffixed with `Props`, defined per component
- **Pages vs Components:**
  - **Pages** (in `pages/`): Inject services, manage state, handle routing
  - **Components** (in `components/`): Props only, no data fetching, fully reusable
- **State management:**
  - `useState` for local UI state
  - Zustand for shared client state
  - TanStack Query for server state
- **Forms:** React Hook Form + Zod schemas
- **i18n:** `useTranslation()` hook — no hardcoded strings
- **Naming:** `camelCase` files/functions, `PascalCase` components/types

#### FastAPI (Backend)

```python
# Router pattern
from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import AssessmentCreate, AssessmentResponse
from .service import AssessmentService
from ..auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/assessments", tags=["assessments"])

@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    service: AssessmentService = Depends(),
) -> AssessmentResponse:
    require_role(current_user, ["super_admin"])
    return await service.create(data, current_user)
```

**Rules:**
- **Async everywhere** — all endpoints, services, DB queries use `async/await`
- **Pydantic v2** for all request/response schemas
- **Dependency injection** — use FastAPI `Depends()` for services, auth, DB sessions
- **SQLAlchemy 2.0 async** — `select()` style, no legacy `.query` API
- **Alembic** for migrations — auto-generate, then review and edit
- **Service layer** — business logic in `service.py`, NOT in route handlers
- **Tenant isolation** — every query filters by `organization_id`
- **Type hints** — all function signatures fully typed
- **Error handling** — custom exception classes + global exception handlers

#### Pydantic Schema Pattern

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class AssessmentCreate(BaseModel):
    organization_id: UUID
    domain_ids: list[int] = Field(..., min_length=1, max_length=9)
    weights: dict[int, float]  # domain_id -> weight (must sum to 100)
    deadline: datetime

class AssessmentResponse(BaseModel):
    id: UUID
    status: str
    overall_score: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

### Translation Keys

**Frontend** (`src/frontend/src/i18n/`):
```json
// ar.json
{
  "assessment": {
    "title": "تقييم النضج الوظيفي",
    "submit": "إرسال التقييم"
  }
}

// en.json
{
  "assessment": {
    "title": "HR Maturity Assessment",
    "submit": "Submit Assessment"
  }
}
```

**Usage:**
```tsx
const { t } = useTranslation();
return <h1>{t('assessment.title')}</h1>;
```

---

## 6. Getting Started

### Prerequisites

- **Python:** 3.12+ (required for SQLAlchemy 2.0 async)
- **Node.js:** 20+ (for Vite 6)
- **Docker:** Latest (for PostgreSQL + Redis)
- **Git:** Latest

### Environment Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd POC
```

#### 2. Copy Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your local settings:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nudj_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (for development)
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=<your-mailtrap-user>
SMTP_PASSWORD=<your-mailtrap-password>

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api
```

#### 3. Start Infrastructure (Docker)
```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)

#### 4. Backend Setup

```bash
cd src/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: `http://localhost:8000/api`
- Docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

#### 5. Frontend Setup

```bash
cd src/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

#### 6. Verify Setup

**Test backend health:**
```bash
curl http://localhost:8000/api/health
```

**Test frontend:**
Open `http://localhost:5173` in browser

### Default Login Credentials

After running migrations, create a super admin user:

```bash
cd src/backend
python -m scripts.create_superuser  # If script exists
# OR manually via API POST /api/auth/register with role=super_admin
```

---

## 7. Key Documentation References

All documentation lives in the project root and `docs/` folder:

| File | Purpose |
|------|---------|
| **`PROJECT_CONTEXT.md`** | Complete platform architecture, business rules, scoring formulas, NFRs |
| **`CLAUDE.md`** | Development conventions (React/FastAPI patterns) — READ THIS FIRST |
| **`docs/USER_JOURNEY_MAP_v2.md`** | 4 persona journeys × 6 stages, critical pain points, 46+ design opportunities |
| **`docs/handoff_guide.md`** | This file — onboarding guide for new developers |
| **`PRD_Tharwah_HR_Maturity_Assessment_Platform_v1.0 1.docx`** | V1 PRD (core platform) |
| **`PRD_Nudj_HR_Maturity_Platform_v2.0.docx`** | V2 PRD (adds BDW, AI Coach, Industry Reporting) |
| **`.env.example`** | Environment variable template |
| **`docker-compose.yml`** | Local infrastructure setup |

### Critical Reading Order

For new developers joining the project:

1. **Start here:** `docs/handoff_guide.md` (this file)
2. **Understand architecture:** `PROJECT_CONTEXT.md`
3. **Learn conventions:** `CLAUDE.md`
4. **Explore user needs:** `docs/USER_JOURNEY_MAP_v2.md`
5. **Deep dive requirements:** PRD v1.0 + v2.0

---

## 8. Multi-Agent Pipeline

This project uses an AI agent pipeline for feature development. Agents coordinate via files in `pipeline/`.

### Agent Roles

| Agent | File | Purpose | Input | Output |
|-------|------|---------|-------|--------|
| **requirements-analyst** | `.claude/agents/requirements-analyst.md` | Parse PRDs into structured requirements | PRD documents | `pipeline/requirements/*.json` |
| **task-splitter** | `.claude/agents/task-splitter.md` | Decompose requirements into parallel tasks | `pipeline/requirements/*.json` | `pipeline/tasks/*-task.md` |
| **coder** | `.claude/agents/coder.md` | Implement specific tasks following conventions | `pipeline/tasks/*-task.md` | `pipeline/tasks/*-result.md` + code |
| **code-reviewer** | `.claude/agents/code-reviewer.md` | Review code quality and architecture | Code + task results | `pipeline/reviews/*-code-review.md` |
| **security-reviewer** | `.claude/agents/security-reviewer.md` | Security review (OWASP, PDPL, tenant isolation) | Code + task results | `pipeline/reviews/*-security-review.md` |

### Pipeline Workflow

```
PRD → requirements-analyst → pipeline/requirements/
    → task-splitter → pipeline/tasks/*-task.md
    → coder → code + pipeline/tasks/*-result.md
    → code-reviewer + security-reviewer → pipeline/reviews/
```

### Pipeline Artifacts

```
pipeline/
├── requirements/          # Structured requirements (JSON)
│   └── feature-name.json
├── tasks/                 # Task manifests and results
│   ├── TASK-001-task.md
│   └── TASK-001-result.md
└── reviews/               # Code and security review findings
    ├── feature-name-code-review.md
    └── feature-name-security-review.md
```

### Agent Coordination Rules

1. **File ownership boundaries** — No two tasks should modify the same file (tracked in `filesOwned` in task manifests)
2. **Sequential dependencies** — Tasks with dependencies run after their blockers complete
3. **Parallel execution** — Independent tasks can run in parallel
4. **Convention adherence** — All agents MUST read `CLAUDE.md` before generating code
5. **Context loading** — Agents read `PROJECT_CONTEXT.md` to understand business rules

---

## Next Steps

### For New Developers

1. Complete environment setup (Section 6)
2. Read `PROJECT_CONTEXT.md` to understand business rules
3. Read `CLAUDE.md` to learn coding conventions
4. Explore the codebase:
   - Backend: Start with `src/backend/app/auth/` to understand RBAC
   - Frontend: Start with `src/frontend/src/features/auth/` to see React patterns
   - Study `src/backend/app/assessments/scoring.py` to understand scoring engine
5. Pick a small task:
   - Fix a bug listed in `pipeline/reviews/`
   - Add a missing translation key in `ar.json`/`en.json`
   - Write a missing test in `tests/`

### For AI Agents

1. Identify your role in `.claude/agents/`
2. Read `PROJECT_CONTEXT.md` + `CLAUDE.md`
3. Load your task from `pipeline/tasks/`
4. Study similar existing implementations before writing new code
5. Follow the implementation protocol in your agent definition
6. Write results to `pipeline/tasks/*-result.md`

### For Project Leads

1. Review `docs/USER_JOURNEY_MAP_v2.md` for UX priorities
2. Check `pipeline/reviews/` for code/security findings
3. Update PRDs in project root when requirements change
4. Ensure all agents have access to updated `CLAUDE.md` conventions

---

## Contact & Support

For questions about this project:
- **Architecture:** See `PROJECT_CONTEXT.md`
- **Conventions:** See `CLAUDE.md`
- **User Needs:** See `docs/USER_JOURNEY_MAP_v2.md`
- **Agent Pipeline:** See `.claude/agents/` definitions

---

**Last Updated:** 2026-02-09
**Version:** 1.0.0
**Status:** V1 Complete, V2 Planning Phase

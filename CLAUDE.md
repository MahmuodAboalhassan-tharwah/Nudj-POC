# Nudj Platform — Development Conventions

## Project Overview

This is the **Nudj (نُضْج) HR Maturity Assessment Platform** POC. Read `PROJECT_CONTEXT.md` for full platform details.

## Development Pipeline

This project uses a multi-agent pipeline. Agents are defined in `.claude/agents/`:

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `requirements-analyst` | Parse PRDs into structured requirements | First — when starting a new feature |
| `task-splitter` | Decompose requirements into parallel coding tasks | After requirements are analyzed |
| `coder` | Implement specific tasks following conventions | After tasks are split |
| `code-reviewer` | Review code quality and architecture | After coding is complete |
| `security-reviewer` | Security-focused review (OWASP, PDPL, tenant isolation) | After coding is complete |

### Pipeline Artifacts

All inter-agent data flows through `pipeline/`:
- `pipeline/requirements/` — Structured requirements (JSON)
- `pipeline/tasks/` — Task manifests and results
- `pipeline/reviews/` — Code and security review findings

## Tech Stack

- **Frontend:** React 19 (TypeScript strict), Vite 6 with SSR, Zustand, TanStack Query, TailwindCSS 4, react-i18next
- **Backend:** FastAPI (async Python 3.12+), SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL, Redis, Celery, Kafka
- **i18n:** Arabic-first bilingual (ar/en), full RTL support

## Frontend Conventions (React + Vite SSR)

### File Structure
```
src/frontend/
├── index.html
├── vite.config.ts
├── server.ts                    # Vite SSR entry (Express/Fastify)
├── entry-client.tsx             # Client hydration entry
├── entry-server.tsx             # Server render entry
├── src/
│   ├── app.tsx                  # Root component + providers
│   ├── router.tsx               # Route definitions
│   ├── features/
│   │   └── <feature>/
│   │       ├── pages/           # Route-level components (smart)
│   │       │   └── <page-name>.tsx
│   │       ├── components/      # Presentational components (dumb)
│   │       │   └── <component-name>.tsx
│   │       ├── hooks/           # Feature-specific custom hooks
│   │       │   └── use-<name>.ts
│   │       ├── api/             # TanStack Query hooks + API calls
│   │       │   └── <feature>.api.ts
│   │       ├── store/           # Zustand store slice (if needed)
│   │       │   └── <feature>.store.ts
│   │       └── types/           # TypeScript interfaces/types
│   │           └── <feature>.types.ts
│   ├── shared/
│   │   ├── components/          # Shared UI components
│   │   ├── hooks/               # Shared custom hooks
│   │   ├── layouts/             # Layout components
│   │   ├── lib/                 # Utilities (api client, auth, etc.)
│   │   └── types/               # Shared TypeScript types
│   ├── i18n/
│   │   ├── ar.json              # Arabic translations
│   │   └── en.json              # English translations
│   └── styles/
│       └── globals.css          # Tailwind + global styles
├── public/                      # Static assets
└── tests/
    └── <feature>/               # Tests mirror src/ structure
```

### Component Rules

**Pages (Smart Components)** — in `pages/`:
- Fetch data (TanStack Query hooks)
- Manage local state
- Handle routing/navigation
- Compose presentational components

**Components (Presentational)** — in `components/`:
- Receive data via props only
- No data fetching, no direct store access
- Emit events via callback props
- Fully reusable and testable

### React Patterns

```tsx
// Named exports only — no default exports
export function AssessmentCard({ score, domain, onSelect }: AssessmentCardProps) {
  // ...
}

// Props interface above or colocated with component
interface AssessmentCardProps {
  score: number;
  domain: string;
  onSelect: (domainId: string) => void;
}
```

- **Named exports** only — no `export default`
- **Function components** only — no class components
- **TypeScript strict** — no `any`, explicit return types on public APIs
- **Props interfaces** — defined per component, suffixed with `Props`
- **Custom hooks** — extract logic into `use<Name>` hooks, prefixed with `use`
- **Memoization** — use `React.memo`, `useMemo`, `useCallback` only when profiled
- **State:** local `useState` for UI state, Zustand for shared client state, TanStack Query for server state
- **Forms:** React Hook Form + Zod schemas for validation
- **i18n:** `useTranslation()` hook — no hardcoded strings
- **Naming:** `camelCase` for files/functions, `PascalCase` for components/types, `kebab-case` for CSS classes

### SSR Rules (Vite)
- Data loading via React Router loaders or TanStack Query with SSR prefetch
- No `window`/`document` access in server-rendered code paths
- Use `useEffect` for client-only side effects
- Hydration-safe: server and client must render identical initial HTML

### Translation
- Every UI string needs keys in both `ar.json` and `en.json`
- Use `useTranslation()` hook with namespace prefixes: `t('assessment.title')`
- RTL layout handled via `dir="rtl"` on root + Tailwind RTL utilities

## Backend Conventions (FastAPI)

### File Structure
```
src/backend/
├── main.py                      # FastAPI app factory + middleware
├── config.py                    # Settings via pydantic-settings
├── database.py                  # SQLAlchemy async engine + session
├── dependencies.py              # Shared FastAPI dependencies
├── alembic/                     # Database migrations
│   ├── alembic.ini
│   └── versions/
├── app/
│   ├── auth/                    # Authentication module
│   │   ├── router.py            # FastAPI router (endpoints)
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── service.py           # Business logic
│   │   ├── dependencies.py      # Auth-specific dependencies
│   │   └── exceptions.py        # Custom exceptions
│   ├── assessments/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── scoring.py           # Scoring engine
│   │   └── exceptions.py
│   ├── organizations/
│   ├── dashboards/
│   ├── reports/
│   ├── notifications/
│   ├── benchmark/               # BDW + ETL (V2)
│   ├── ai_coach/                # AI Coach (V2)
│   └── common/
│       ├── models.py            # Base models (TimestampMixin, etc.)
│       ├── schemas.py           # Shared schemas (pagination, errors)
│       ├── exceptions.py        # Base exceptions + handlers
│       ├── middleware.py         # Tenant isolation, logging, etc.
│       └── utils.py
├── tasks/                       # Celery tasks
│   ├── celery_app.py
│   ├── email_tasks.py
│   └── etl_tasks.py
└── tests/
    ├── conftest.py              # Fixtures (async db, test client)
    └── <module>/
        ├── test_router.py
        ├── test_service.py
        └── test_models.py
```

### FastAPI Rules

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

- **Async everywhere** — all endpoints, services, and DB queries are async
- **Pydantic v2** — all request/response schemas use Pydantic BaseModel
- **Dependency injection** — use FastAPI `Depends()` for services, auth, DB sessions
- **SQLAlchemy 2.0** async style — `select()`, `async_session`, no legacy query API
- **Alembic** for migrations — auto-generate, then review and edit
- **Router per module** — each module has its own `router.py` included in `main.py`
- **Service layer** — business logic in `service.py`, not in route handlers
- **Tenant isolation** — every query filters by `organization_id` via middleware/dependency
- **Error handling** — custom exception classes + global exception handlers
- **Type hints** — all function signatures fully typed, mypy strict

### Pydantic Schema Rules

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

### Testing

- **Vitest** + React Testing Library for frontend
- **pytest** + pytest-asyncio + httpx for backend
- Every component needs a `.test.tsx`
- Every router/service needs `test_*.py`
- Use fixtures for DB setup/teardown (`conftest.py`)
- Test tenant isolation explicitly

## Security

- No hardcoded secrets or credentials — use environment variables
- Tenant isolation on every data access (organization_id filter)
- OWASP Top 10 protections
- PDPL compliance for personal data
- NCA ECC standards for encryption
- File upload validation (magic bytes + size + virus scan)
- JWT with short-lived access tokens + refresh tokens
- Rate limiting on auth and AI Coach endpoints

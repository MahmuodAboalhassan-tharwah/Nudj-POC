# Nudj Project Handoff & Developer Guide

## 1. Project Overview
**Nudj** is a bilingual (English/Arabic) HR Maturity Assessment Platform. It allows organizations to assess their HR practices against a standardized framework, receive scores, and collaborate on improvements.

### Tech Stack
- **Backend**: Python (FastAPI), SQLAlchemy (Async), Alembic (Migrations), Pydantic.
- **Frontend**: TypeScript (React + Vite), Tailwind CSS, Shadcn UI, React Query, React Router.
- **Database**: PostgreSQL.
- **Infrastructure**: Docker (implied), local dev environment.

## 2. Critical Artifacts (READ THESE FIRST)
To understand the current state and history of the project, you **MUST** read these files in the `brain` directory:

1.  **`task.md`**: The master checklist. It tracks every feature from Phase 1 (Auth) to Phase 16 (Admin Refinement).
    *   *Usage*: Check this to see what was just finished and what is pending.
2.  **`walkthrough.md`**: A detailed log of *what* was implemented and *how*.
    *   *Usage*: Read this to understand the implementation details of existing features (e.g., how the weird recursive comment threading works).
3.  **`implementation_plan.md`**: The design document for the most recent or active task.
    *   *Usage*: Always update this before starting a new major feature.

## 3. Codebase Navigation Map

### Backend (`src/backend/app`)
The backend is modular. Each folder in `app` is a self-contained domain:
- **`auth/`**: User, Role, Permission logic. `permissions.py` is critical for RBAC.
- **`assessments/`**: The core domain.
    - `models.py`: `Assessment`, `AssessmentDomain`, `AssessmentElementResponse`.
    - `service.py`: Complex logic for creating assessments and calculating scores.
- **`framework/`**: Configuration for domain weights (`FrameworkDomainConfig`).
- **`organization/`**: Tenant management.
- **`notifications/`**: Notification system (`NotificationService`).
- **`reporting/`**: PDF generation and data aggregation.

### Frontend (`src/frontend/src`)
Feature-based architecture:
- **`features/`**: Contains all business logic and UI pages.
    - `auth/`: Login, Register, SSO.
    - `assessments/`: The main questionnaire UI (`AssessmentDetailPage`).
    - `admin/`: Super Admin consoles (Users, Orgs, Framework Config).
    - `dashboard/`: Charts and widgets.
- **`shared/`**: Reusable components (`ui/`), hooks, and config.
- **`app/router.tsx`**: Central routing file. **Always** looking here to see how pages are wired up and protected by `RoleGuard`.

## 4. Development Workflow & Philosophy
When adding features, strictly follow this cycle:

1.  **Plan**: Create/Update `implementation_plan.md`. Get user approval.
2.  **Task**: Update `task.md` to mark the item as "in progress".
3.  **Implement**: Write code.
    - **Bilingual Rule**: NEVER hardcode text. Always add keys to `en.json` and `ar.json` immediately.
    - **Security Rule**: Always check role permissions on both Backend (Dependencies) and Frontend (`RoleGuard`).
4.  **Verify**: Run tests (if available) or verify manually.
5.  **Document**: Update `walkthrough.md` with what you built.
6.  **Complete**: Mark `task.md` as `[x]`.

## 5. Key Context for Next Steps
- **Completed**: Implementation of all core V1 features (Auth, Assessment, Org, Dashboard, Reporting, Admin).
- **Recent Work**: Added "Framework Weight Configuration" (Task 902) and performed a "Final Deployment Readiness Audit" (Task 903).
- **Environment**: The project uses `.env` files. `config.py` in backend validates these.

## 6. How to Start
1.  Read `task.md` to confirm the current phase.
2.  If asked to build a new feature, start by drafting an `implementation_plan.md`.
3.  If asked to fix a bug, look at `walkthrough.md` to see how that component was built.

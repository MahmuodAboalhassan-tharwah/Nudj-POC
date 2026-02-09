# Code Review: Dashboards & Reporting

## Overview
- **Feature**: Dashboards (Portfolio/Client) & Reporting (PDF)
- **Reviewer**: AI Assistant
- **Date**: 2026-02-08

## Findings

### Backend
1.  **Router Structure**: `dashboards/router.py` and `reports/router.py` follow RESTful conventions.
2.  **Type Safety**: Pydantic models in `schemas.py` provide good type safety for API responses.
3.  **Refactoring Opportunity**: `DashboardService` methods could potentially share more aggregation logic, but separation is fine for now given different schemas.
4.  **Error Handling**: Basic error handling (404, 403) is present.
5.  **PDF Generation**: `weasyprint` is a heavy dependency but standard for this use case. Template loading in `generator.py` uses `FileSystemLoader` which is correct.

### Frontend
1.  **Component Modularity**: `StatsCard` and `RecentAssessments` are well-separated.
2.  **API Integration**: `usePortfolioDashboard` and `useClientDashboard` hooks correctly wrap API calls.
3.  **PDF Download**: `DownloadReportButton` allows binary blob download and url creation.
    *   *Note*: `window.URL.revokeObjectURL(url)` is correctly called to prevent memory leaks.
4.  **Type Safety**: Types are defined in `dashboard.types.ts`.

### Suggestions
- **Backend**: Add unit tests for `ReportingService` aggregation logic.
- **Frontend**: Add error toast notification if download fails (currently just `console.error`).
- **Frontend**: `SuperAdminDashboard` has a hardcoded placeholder for the chart. Ensure this is replaced with a real library (e.g., Recharts) in the next iteration.

## Conclusion
Code is structured well and follows project patterns. **Approved**.

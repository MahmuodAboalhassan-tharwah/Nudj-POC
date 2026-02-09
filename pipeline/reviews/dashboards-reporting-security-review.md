# Security Review: Dashboards & Reporting

## Overview
- **Feature**: Dashboards & Reporting
- **Reviewer**: AI Assistant
- **Date**: 2026-02-08

## Findings

### Authorization (RBAC)
- **Portfolio Dashboard**: correctly restricted to `SUPER_ADMIN` (`current_user.role != Role.SUPER_ADMIN` check).
- **Client Dashboard**: logic allows `SUPER_ADMIN` OR `CLIENT_ADMIN` of the specific Organization.
    *   *Check*: `current_user.organization_id != str(org_id)` ensures users can't access other orgs' dashboards.
- **Reporting**:
    *   *Current State*: `download_assessment_report` in `reports/router.py` lacks explicit RBAC check for the *specific* assessment's organization ownership. It relies on the user being authenticated.
    *   *Risk*: A user from Org A could potentially guess an Assessment ID from Org B and download the report.
    *   *Remediation Required*: Add a check in `ReportingService` or `router` to ensure `assessment.organization_id == current_user.organization_id` (unless Super Admin).

### Input Validation
- UUIDs are validated by FastAPI type checking.

### Output Encoding
- **HTML/PDF**: `jinja2` auto-escapes by default, reducing XSS risk in generated PDFs if user input (e.g., comments) is included.

### Data Privacy
- **PDF Content**: Contains sensitive HR maturity data. Ensure generated PDFs are not cached publicly or accessible via static URLs. The current implementation streams them directly, which is good.

## Conclusion
**Conditional Approval**.
**Action Item**: Fix the missing ownership check in `reports/router.py` or `service.py` to prevent IDOR (Insecure Direct Object Reference) on reports.

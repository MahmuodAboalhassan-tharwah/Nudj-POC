# Comprehensive Testing Plan - Nudj Platform

**Status**: Draft
**Date**: 2026-02-09
**Version**: 1.0

---

## Overview

This document outlines the comprehensive testing strategy for the Nudj Platform, covering:
- Unit tests for individual components
- Integration tests for feature workflows
- End-to-end tests for cross-feature interactions
- Security and compliance testing

## Testing Framework Stack

### Backend (FastAPI)
- **pytest** - Test runner
- **pytest-asyncio** - Async test support
- **httpx** - HTTP client for API testing
- **pytest-cov** - Code coverage
- **faker** - Test data generation
- **freezegun** - Time mocking for time-sensitive tests

### Frontend (React)
- **Vitest** - Test runner (faster than Jest)
- **React Testing Library** - Component testing
- **MSW (Mock Service Worker)** - API mocking
- **@testing-library/user-event** - User interaction simulation
- **vitest-axe** - Accessibility testing

---

## 1. Unit Tests

Unit tests verify individual functions, classes, and components in isolation.

### Backend Unit Tests

#### 1.1 Authentication Module (`src/backend/app/auth/`)

**File**: `tests/auth/test_password_service.py`
```python
class TestPasswordService:
    def test_hash_password_returns_bcrypt_hash()
    def test_verify_password_success()
    def test_verify_password_failure()
    def test_password_strength_validation()
    def test_common_passwords_rejected()
```

**File**: `tests/auth/test_jwt_service.py`
```python
class TestJWTService:
    def test_create_access_token()
    def test_create_refresh_token()
    def test_verify_access_token_success()
    def test_verify_access_token_expired()
    def test_verify_access_token_invalid_signature()
    def test_token_payload_contains_required_fields()
```

**File**: `tests/auth/test_mfa_service.py`
```python
class TestMFAService:
    def test_generate_secret()
    def test_generate_qr_code_uri()
    def test_verify_totp_code_success()
    def test_verify_totp_code_expired()
    def test_verify_totp_code_with_tolerance_window()
    def test_generate_backup_codes()
    def test_verify_backup_code_single_use()
```

**File**: `tests/auth/test_permissions.py`
```python
class TestPermissionService:
    def test_get_permissions_for_super_admin()
    def test_get_permissions_for_analyst()
    def test_get_permissions_for_client_admin()
    def test_get_permissions_for_assessor()
    def test_can_manage_role_hierarchy()
    def test_tenant_isolation_permissions()
```

#### 1.2 Organizations Module

**File**: `tests/organizations/test_service.py`
```python
class TestOrganizationService:
    async def test_create_organization()
    async def test_list_organizations_pagination()
    async def test_get_organization_by_id()
    async def test_update_organization()
    async def test_delete_organization_soft_delete()
```

#### 1.3 Assessments Module

**File**: `tests/assessments/test_scoring.py`
```python
class TestScoringEngine:
    def test_element_score_calculation()
    def test_dimension_score_weighted_average()
    def test_domain_score_calculation()
    def test_overall_score_weighted_sum()
    def test_maturity_level_determination()
```

**File**: `tests/assessments/test_validation.py`
```python
class TestAssessmentValidation:
    def test_weights_must_sum_to_100()
    def test_all_9_domains_required()
    def test_deadline_must_be_future()
    def test_organization_must_exist()
```

#### 1.4 Notifications Module

**File**: `tests/notifications/test_email_service.py`
```python
class TestEmailService:
    async def test_send_email_success()
    async def test_send_email_with_template()
    async def test_email_mock_mode_in_development()
    async def test_smtp_configuration()
    async def test_sendgrid_configuration()
```

#### 1.5 Common Utilities

**File**: `tests/common/test_audit_service.py`
```python
class TestAuditService:
    async def test_log_event()
    async def test_query_logs_with_filters()
    async def test_query_logs_pagination()
    async def test_export_csv()
    async def test_get_security_stats()
```

### Frontend Unit Tests

#### 1.6 Authentication Components

**File**: `tests/features/auth/components/LoginForm.test.tsx`
```typescript
describe('LoginForm', () => {
  it('renders email and password fields')
  it('validates email format')
  it('validates password required')
  it('shows MFA input when requires_mfa is true')
  it('submits form with correct credentials')
  it('displays error messages')
})
```

#### 1.7 Custom Hooks

**File**: `tests/features/auth/hooks/useAuth.test.ts`
```typescript
describe('useAuth', () => {
  it('returns current user from store')
  it('logs in user and stores tokens')
  it('logs out user and clears tokens')
  it('refreshes token when expired')
  it('handles MFA flow')
})
```

---

## 2. Integration Tests

Integration tests verify complete workflows across multiple components.

### Backend Integration Tests

#### 2.1 Authentication Workflows

**File**: `tests/integration/test_auth_flow.py`
```python
class TestAuthenticationFlow:
    async def test_complete_login_flow()
    async def test_login_with_mfa_flow()
    async def test_password_reset_flow()
    async def test_token_refresh_flow()
    async def test_logout_flow()
    async def test_account_lockout_after_failed_attempts()
```

#### 2.2 User Management Workflows

**File**: `tests/integration/test_user_management.py`
```python
class TestUserManagement:
    async def test_invite_user_flow()
    async def test_complete_registration_via_invitation()
    async def test_deactivate_and_reactivate_user()
    async def test_change_user_role()
    async def test_bulk_invite_users()
```

#### 2.3 Assessment Workflows

**File**: `tests/integration/test_assessment_flow.py`
```python
class TestAssessmentFlow:
    async def test_create_assessment_as_client_admin()
    async def test_delegate_assessment_to_assessor()
    async def test_complete_assessment_questions()
    async def test_calculate_scores_on_completion()
    async def test_generate_pdf_report()
```

#### 2.4 Organization Workflows

**File**: `tests/integration/test_organization_flow.py`
```python
class TestOrganizationFlow:
    async def test_create_org_and_admin_user()
    async def test_add_multiple_assessors_to_org()
    async def test_org_deletion_cascades_correctly()
```

### Frontend Integration Tests

#### 2.5 Authentication Pages

**File**: `tests/integration/auth/LoginPage.integration.test.tsx`
```typescript
describe('LoginPage Integration', () => {
  it('logs in successfully and redirects to dashboard')
  it('handles MFA verification flow')
  it('shows error for invalid credentials')
  it('locks account after 5 failed attempts')
})
```

#### 2.6 Admin User Management

**File**: `tests/integration/admin/UserManagement.integration.test.tsx`
```typescript
describe('User Management Integration', () => {
  it('invites new user and sends email')
  it('displays paginated user list')
  it('updates user role and persists changes')
  it('deactivates user and prevents login')
})
```

---

## 3. End-to-End (E2E) Tests

E2E tests verify complete user journeys across frontend and backend.

### Tool: Playwright

**File**: `tests/e2e/auth.spec.ts`
```typescript
test.describe('Authentication E2E', () => {
  test('Complete registration via invitation', async ({ page }) => {
    // 1. Admin sends invitation
    // 2. User receives email (mocked)
    // 3. User clicks link and registers
    // 4. User logs in
    // 5. Verify dashboard access
  })

  test('Login with MFA', async ({ page }) => {
    // 1. User logs in with email/password
    // 2. MFA screen appears
    // 3. User enters TOTP code
    // 4. Access granted
  })
})
```

**File**: `tests/e2e/assessment.spec.ts`
```typescript
test.describe('Assessment E2E', () => {
  test('Complete assessment lifecycle', async ({ page }) => {
    // 1. Client Admin creates assessment
    // 2. Delegates to Assessor
    // 3. Assessor completes questions
    // 4. Scores calculated automatically
    // 5. Report generated
    // 6. Client Admin views report
  })
})
```

---

## 4. Cross-Feature Integration Tests

These tests verify interactions between multiple features.

### 4.1 Assessment + Notifications

**File**: `tests/cross_feature/test_assessment_notifications.py`
```python
class TestAssessmentNotifications:
    async def test_delegation_sends_notification()
    async def test_completion_sends_email()
    async def test_report_ready_notification()
```

### 4.2 Auth + Audit Logs

**File**: `tests/cross_feature/test_auth_audit.py`
```python
class TestAuthAudit:
    async def test_login_success_logged()
    async def test_login_failure_logged()
    async def test_mfa_events_logged()
    async def test_role_change_logged()
```

### 4.3 Organizations + Tenant Isolation

**File**: `tests/cross_feature/test_tenant_isolation.py`
```python
class TestTenantIsolation:
    async def test_client_admin_only_sees_own_org_users()
    async def test_assessor_only_sees_own_org_assessments()
    async def test_super_admin_sees_all_orgs()
    async def test_cross_org_access_blocked()
```

### 4.4 Dashboards + Data Aggregation

**File**: `tests/cross_feature/test_dashboard_data.py`
```python
class TestDashboardData:
    async def test_analyst_dashboard_shows_all_orgs()
    async def test_client_admin_dashboard_shows_own_org_only()
    async def test_assessor_dashboard_shows_assigned_assessments()
    async def test_dashboard_metrics_calculated_correctly()
```

---

## 5. Security & Compliance Tests

### 5.1 Authentication Security

**File**: `tests/security/test_auth_security.py`
```python
class TestAuthSecurity:
    async def test_passwords_hashed_with_bcrypt()
    async def test_jwt_tokens_signed_correctly()
    async def test_refresh_token_rotation()
    async def test_rate_limiting_on_login()
    async def test_account_lockout_mechanism()
```

### 5.2 Tenant Isolation

**File**: `tests/security/test_tenant_isolation.py`
```python
class TestTenantIsolationSecurity:
    async def test_org_a_cannot_access_org_b_data()
    async def test_assessor_cannot_escalate_to_admin()
    async def test_client_admin_cannot_access_other_orgs()
```

### 5.3 Input Validation

**File**: `tests/security/test_input_validation.py`
```python
class TestInputValidation:
    async def test_sql_injection_prevention()
    async def test_xss_prevention_in_responses()
    async def test_file_upload_validation()
    async def test_email_validation()
```

### 5.4 PDPL Compliance

**File**: `tests/compliance/test_pdpl.py`
```python
class TestPDPLCompliance:
    async def test_audit_logs_retained_5_years()
    async def test_user_data_export()
    async def test_user_data_deletion()
    async def test_consent_tracking()
```

---

## 6. Test Data Management

### Fixtures (`tests/conftest.py`)

```python
@pytest.fixture
async def db_session():
    """Provide clean database session for each test."""

@pytest.fixture
async def test_client():
    """Provide authenticated HTTP client."""

@pytest.fixture
async def super_admin_user():
    """Create test super admin user."""

@pytest.fixture
async def test_organization():
    """Create test organization."""

@pytest.fixture
async def test_assessment():
    """Create test assessment with sample questions."""
```

### Factory Pattern

**File**: `tests/factories.py`
```python
class UserFactory:
    @staticmethod
    def create(role: Role = Role.ASSESSOR, **kwargs) -> User:
        """Create test user with defaults."""

class OrganizationFactory:
    @staticmethod
    def create(**kwargs) -> Organization:
        """Create test organization."""

class AssessmentFactory:
    @staticmethod
    def create(**kwargs) -> Assessment:
        """Create test assessment."""
```

---

## 7. Test Execution Plan

### Phase 1: Critical Path Tests (Week 1)
- [ ] Authentication unit tests
- [ ] JWT service tests
- [ ] MFA service tests
- [ ] Login integration tests

### Phase 2: Feature Tests (Week 2)
- [ ] Organizations module tests
- [ ] User management tests
- [ ] Assessments scoring tests
- [ ] Notifications tests

### Phase 3: Cross-Feature Tests (Week 3)
- [ ] Tenant isolation tests
- [ ] Audit logging tests
- [ ] Dashboard data tests
- [ ] Assessment + notifications tests

### Phase 4: E2E & Security (Week 4)
- [ ] Playwright E2E tests
- [ ] Security vulnerability tests
- [ ] PDPL compliance tests
- [ ] Performance tests

---

## 8. Coverage Goals

| Module | Target Coverage | Priority |
|--------|----------------|----------|
| Authentication | 95%+ | Critical |
| Authorization | 95%+ | Critical |
| Assessments | 90%+ | High |
| Organizations | 90%+ | High |
| Notifications | 85%+ | Medium |
| Dashboards | 85%+ | Medium |
| Reports | 80%+ | Medium |

### Coverage Command

```bash
# Backend
pytest --cov=src/backend --cov-report=html --cov-report=term

# Frontend
npm run test:coverage
```

---

## 9. Continuous Integration

### GitHub Actions Workflow

**File**: `.github/workflows/test.yml`
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v4
      - name: Run Backend Tests
        run: |
          pip install -r requirements.txt
          pytest --cov=src/backend

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Frontend Tests
        run: |
          npm ci
          npm run test:ci
```

---

## 10. Test Documentation Standards

### Test Naming Convention

```python
# Format: test_<what>_<when>_<expected>
def test_login_with_invalid_password_returns_401()
def test_assessment_completion_sends_notification()
def test_client_admin_cannot_access_other_org_data()
```

### AAA Pattern (Arrange-Act-Assert)

```python
async def test_create_assessment():
    # Arrange
    user = await create_test_user(role=Role.CLIENT_ADMIN)
    org = await create_test_organization()

    # Act
    assessment = await assessment_service.create(...)

    # Assert
    assert assessment.status == AssessmentStatus.DRAFT
    assert assessment.organization_id == org.id
```

---

## 11. Implementation Checklist

### Setup Phase
- [ ] Install testing dependencies (pytest, vitest, playwright)
- [ ] Configure test databases (separate from dev)
- [ ] Set up fixtures and factories
- [ ] Configure coverage reporting

### Backend Tests
- [ ] Auth module: password, JWT, MFA services
- [ ] Auth module: login, registration, logout flows
- [ ] Organizations: CRUD operations
- [ ] Assessments: scoring engine, validation
- [ ] Notifications: email sending
- [ ] Audit logs: logging and querying
- [ ] Tenant isolation: cross-org access prevention

### Frontend Tests
- [ ] Auth components: LoginForm, RegisterForm
- [ ] Admin pages: UserManagement, AuditLogs
- [ ] Assessment pages: CreateAssessment, TakeAssessment
- [ ] Dashboard components: metrics, charts
- [ ] Custom hooks: useAuth, usePermissions

### Integration & E2E
- [ ] Authentication flows (login, MFA, password reset)
- [ ] User management flows (invite, register, deactivate)
- [ ] Assessment flows (create, delegate, complete, report)
- [ ] Cross-feature: assessment + notifications
- [ ] Cross-feature: auth + audit logs
- [ ] Cross-feature: tenant isolation

### Security & Compliance
- [ ] OWASP Top 10 vulnerability tests
- [ ] Tenant isolation verification
- [ ] PDPL compliance tests
- [ ] Rate limiting tests
- [ ] Input validation tests

---

## Summary

This testing plan provides comprehensive coverage across:
- ✅ 50+ unit tests for core services
- ✅ 20+ integration tests for workflows
- ✅ 10+ E2E tests for user journeys
- ✅ 15+ security and compliance tests
- ✅ Cross-feature interaction testing
- ✅ 85-95% code coverage targets

**Next Steps:**
1. Run `reactivate_admin.py` to fix admin account
2. Test all fixed endpoints
3. Begin implementing tests in priority order
4. Set up CI/CD pipeline for automated testing

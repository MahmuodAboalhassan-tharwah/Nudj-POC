# Nudj Platform - Frontend Endpoints Reference

**Platform:** Nudj (نُضْج) HR Maturity Assessment Platform
**Version:** V1
**Frontend URL:** http://localhost:5174
**Backend API:** http://localhost:8000
**Date:** 2026-02-09

---

## Table of Contents

1. [Public Routes (Unauthenticated)](#public-routes)
2. [Protected Routes (Authenticated)](#protected-routes)
3. [Backend API Endpoints](#backend-api-endpoints)
4. [Role-Based Access](#role-based-access)
5. [API Integration](#api-integration)

---

## Public Routes (Unauthenticated)

These routes are accessible without authentication:

| Route | Component | Description | Layout |
|-------|-----------|-------------|--------|
| `/login` | LoginPage | User login with email/password | AuthLayout |
| `/register` | RegisterPage | User registration with invitation token | AuthLayout |
| `/invitation-expired` | InvitationExpiredPage | Expired invitation error page | AuthLayout |
| `/sso/callback` | SSOCallbackPage | OAuth callback for SSO (Azure AD, Google) | AuthLayout |

### Query Parameters:

**Registration & Invitation:**
- `/register?token={invitation_token}` - Registration with invitation
- `/invitation-expired?token={expired_token}` - Show expired invitation details

---

## Protected Routes (Authenticated)

All routes below require authentication. Users are redirected to `/login` if not authenticated.

### 1. Dashboard Routes

| Route | Component | Roles | Description |
|-------|-----------|-------|-------------|
| `/` | DashboardRouter | All | Root - Auto-routes based on role |
| `/dashboard` | DashboardRouter | All | Explicit dashboard route |
| - | SuperAdminDashboard | super_admin | Platform-wide analytics & management |
| - | ClientDashboard | analyst, client_admin, assessor | Organization-specific dashboard |

**Auto-Routing Logic:**
- `super_admin` → SuperAdminDashboard
- All others → ClientDashboard

---

### 2. Assessment Routes

| Route | Component | Roles | Description |
|-------|-----------|-------|-------------|
| `/assessments` | AssessmentsPage | All | List all assessments for user's organization |
| `/assessments/:id` | AssessmentDetailPage | All | Assessment details, questions, scoring |

**Dynamic Parameters:**
- `:id` - Assessment UUID

**Features:**
- Create new assessments (CLIENT_ADMIN, SUPER_ADMIN, ANALYST only)
- View assessment progress
- Submit responses
- Upload evidence
- Delegate domains to assessors
- Download PDF reports

---

### 3. Admin - Organizations

| Route | Component | Roles | Description |
|-------|-----------|-------|-------------|
| `/admin/organizations` | OrganizationsPage | super_admin | List all organizations |
| `/admin/organizations/new` | OrganizationDetailPage | super_admin | Create new organization |
| `/admin/organizations/:id` | OrganizationDetailPage | super_admin | Edit organization details |

**Dynamic Parameters:**
- `:id` - Organization UUID

---

### 4. Admin - User Management

| Route | Component | Roles | Description |
|-------|-----------|-------|-------------|
| `/admin/users` | UsersListPage | super_admin, client_admin | User management for organization |

**Role-Specific Access:**
- **super_admin**: Manage all users across all organizations
- **client_admin**: Manage users within their organization only

**Features:**
- Invite users (send invitation emails)
- Edit user roles
- Activate/deactivate users
- View user details
- Bulk invite via CSV

---

### 5. Admin - Audit Logs

| Route | Component | Roles | Description |
|-------|-----------|-------|-------------|
| `/admin/audit-logs` | AuditLogsPage | super_admin | Security and activity audit logs |

**Features:**
- View all system events
- Filter by event type, user, organization, date range
- Export logs to CSV
- Track login attempts, password changes, role changes, etc.

---

### 6. Admin - Framework Configuration

| Route | Component | Roles | Description |
|-------|-----------|-------|-------------|
| `/admin/framework` | FrameworkConfigPage | super_admin | Configure HR maturity framework domains and weights |

**Features:**
- View 9 HR domains (Attracting, Recruiting, etc.)
- Adjust domain weights (must sum to 100%)
- Update domain descriptions
- Enable/disable domains

---

### 7. Catch-All Route

| Route | Redirect | Description |
|-------|----------|-------------|
| `*` (any unmatched) | `/` | Redirects to dashboard |

---

## Backend API Endpoints

These are the REST API endpoints the frontend calls:

### Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | Login with email/password | No |
| POST | `/auth/register` | Register with invitation token | No |
| POST | `/auth/logout` | Logout (invalidate token) | Yes |
| GET | `/auth/me` | Get current user details | Yes |
| POST | `/auth/mfa/verify` | Verify MFA code during login | No |
| GET | `/auth/mfa/setup` | Get MFA QR code for setup | Yes |
| POST | `/auth/mfa/enable` | Enable MFA for account | Yes |
| POST | `/auth/mfa/disable` | Disable MFA for account | Yes |
| POST | `/auth/forgot-password` | Request password reset email | No |
| POST | `/auth/reset-password` | Reset password with token | No |
| POST | `/auth/change-password` | Change password (authenticated) | Yes |
| DELETE | `/auth/sessions` | Revoke all sessions | Yes |

---

### Admin - Users (`/admin/users`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/admin/users` | List users (paginated, filtered) | super_admin, client_admin |
| POST | `/admin/users/invite` | Send invitation email | super_admin, client_admin |
| POST | `/admin/users/invite/bulk` | Bulk invite from CSV | super_admin, client_admin |
| PATCH | `/admin/users/{userId}` | Update user (role, status) | super_admin, client_admin |
| DELETE | `/admin/users/{userId}` | Deactivate user | super_admin |

---

### Admin - Audit Logs (`/admin/audit-logs`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/admin/audit-logs` | List audit logs (paginated, filtered) | super_admin |
| GET | `/admin/audit-logs/export` | Export logs to CSV | super_admin |

---

### Assessments (`/assessments`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/assessments` | List assessments | All |
| POST | `/assessments` | Create new assessment | client_admin, super_admin, analyst |
| GET | `/assessments/{id}` | Get assessment details | All |
| PATCH | `/assessments/{id}` | Update assessment | client_admin, super_admin, analyst |
| DELETE | `/assessments/{id}` | Delete assessment | super_admin |
| GET | `/assessments/{id}/responses` | Get responses for domains | All |
| POST | `/assessments/responses/{responseId}/evidence` | Upload evidence file | All |
| POST | `/assessments/{id}/submit` | Submit for scoring | client_admin, analyst |
| GET | `/assessments/{id}/report` | Download PDF report | All |

---

### Delegations (`/delegations`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/delegations` | List delegations for assessment | All |
| POST | `/delegations` | Delegate domain to assessor | client_admin, super_admin, analyst |
| PATCH | `/delegations/{id}` | Update delegation | client_admin, super_admin, analyst |
| DELETE | `/delegations/{id}` | Remove delegation | client_admin, super_admin, analyst |

---

### Organizations (`/organizations`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/organizations` | List all organizations | super_admin |
| POST | `/organizations` | Create organization | super_admin |
| GET | `/organizations/{id}` | Get organization details | super_admin |
| PATCH | `/organizations/{id}` | Update organization | super_admin |
| DELETE | `/organizations/{id}` | Deactivate organization | super_admin |

---

### Framework (`/framework`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/framework/domains` | List all HR domains | super_admin |
| PATCH | `/framework/domains/{id}` | Update domain weight | super_admin |

---

### Dashboards (`/dashboards`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/dashboards/stats` | Get dashboard statistics | All |
| GET | `/dashboards/portfolio` | Portfolio analytics | super_admin |
| GET | `/dashboards/organization/{orgId}` | Organization analytics | All |

---

### Comments (`/comments`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/comments` | List comments for response | All |
| POST | `/comments` | Add comment to response | All |
| PATCH | `/comments/{id}` | Edit comment | All (owner only) |
| DELETE | `/comments/{id}` | Delete comment | All (owner only) |

---

### Notifications (`/notifications`)

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/notifications` | List user notifications | All |
| GET | `/notifications/unread-count` | Get unread count | All |
| PATCH | `/notifications/{id}/read` | Mark as read | All |
| PATCH | `/notifications/read-all` | Mark all as read | All |

---

## Role-Based Access

### Role Hierarchy:

```
super_admin          (Highest privileges - platform-wide access)
    ↓
client_admin         (Organization admin)
    ↓
analyst              (Can create assessments)
    ↓
assessor             (Can only respond to delegated domains)
```

### Role Permissions Matrix:

| Feature | super_admin | client_admin | analyst | assessor |
|---------|-------------|--------------|---------|----------|
| **Dashboard** |
| View own dashboard | ✅ | ✅ | ✅ | ✅ |
| View platform analytics | ✅ | ❌ | ❌ | ❌ |
| **Organizations** |
| View all organizations | ✅ | ❌ | ❌ | ❌ |
| Create/edit organizations | ✅ | ❌ | ❌ | ❌ |
| **Users** |
| View all users | ✅ | ✅* | ❌ | ❌ |
| Invite users | ✅ | ✅* | ❌ | ❌ |
| Edit user roles | ✅ | ✅* | ❌ | ❌ |
| Delete users | ✅ | ❌ | ❌ | ❌ |
| **Assessments** |
| View assessments | ✅ | ✅ | ✅ | ✅** |
| Create assessments | ✅ | ✅ | ✅ | ❌ |
| Edit assessments | ✅ | ✅ | ✅ | ❌ |
| Delete assessments | ✅ | ❌ | ❌ | ❌ |
| Respond to questions | ✅ | ✅ | ✅ | ✅** |
| Delegate domains | ✅ | ✅ | ✅ | ❌ |
| Download reports | ✅ | ✅ | ✅ | ✅** |
| **Framework** |
| Configure domains/weights | ✅ | ❌ | ❌ | ❌ |
| **Audit Logs** |
| View audit logs | ✅ | ❌ | ❌ | ❌ |
| Export logs | ✅ | ❌ | ❌ | ❌ |

**Notes:**
- `*` - client_admin can only manage users within their own organization
- `**` - assessor can only access assessments/domains delegated to them

---

## API Integration

### Base URL Configuration

**Development:**
```typescript
API_BASE_URL = '/api'  // Proxied by Vite to http://localhost:8000/api
```

**Production:**
```typescript
API_BASE_URL = process.env.VITE_API_BASE_URL || 'https://api.nudj.sa'
```

### Vite Proxy Configuration

Located in `vite.config.ts`:

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

**How it works:**
- Frontend: `http://localhost:5174`
- API calls: `axios.get('/api/auth/me')`
- Proxied to: `http://localhost:8000/api/auth/me`

---

### Authentication Flow

**Login Process:**
1. User submits credentials → `POST /api/auth/login`
2. Backend validates → Returns JWT tokens
3. Frontend stores:
   - `accessToken` in localStorage
   - `refreshToken` in localStorage
4. All subsequent requests include: `Authorization: Bearer {accessToken}`

**Token Refresh:**
- Axios interceptor detects 401 errors
- Automatically calls `POST /api/auth/refresh` with refresh token
- Retries original request with new access token
- On refresh failure → Redirect to `/login`

**Logout:**
- Call `POST /api/auth/logout`
- Clear localStorage
- Redirect to `/login`

---

### Request/Response Interceptors

**Request Interceptor:**
```typescript
apiClient.interceptors.request.use((config) => {
  // Add JWT token
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Add language header for i18n
  const language = localStorage.getItem('language') || 'ar';
  config.headers['Accept-Language'] = language;

  return config;
});
```

**Response Interceptor:**
```typescript
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle 401 - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Attempt token refresh
      const refreshToken = localStorage.getItem('refreshToken');
      const response = await axios.post('/api/auth/refresh', { refresh_token: refreshToken });

      // Retry original request with new token
      return apiClient(originalRequest);
    }

    return Promise.reject(error);
  }
);
```

---

### React Query Integration

All API calls use **TanStack React Query** for:
- Caching
- Background refetching
- Optimistic updates
- Loading/error states

**Query Keys Pattern:**
```typescript
// Feature-based query keys
assessmentKeys = {
  all: ['assessments'],
  lists: () => [...assessmentKeys.all, 'list'],
  detail: (id) => [...assessmentKeys.all, 'detail', id],
  delegations: (id) => [...assessmentKeys.all, 'delegations', id],
};

// Usage
const { data, isLoading } = useQuery({
  queryKey: assessmentKeys.detail(id),
  queryFn: () => apiClient.get(`/assessments/${id}`),
});
```

---

## Testing the Frontend

### Prerequisites:
1. ✅ Node.js v24+ installed
2. ✅ Backend running on port 8000
3. ✅ Database seeded with super admin

### Start Frontend:
```bash
cd c:/Work/PoCs/Nudj-POC/src/frontend
npm run dev
```

**Access:** http://localhost:5174

### Test Credentials:
```
Email: admin@nudj.sa
Password: Nudj@2026Admin
Role: super_admin
```

### Test Flow:
1. ✅ Login at `/login`
2. ✅ Dashboard loads based on role
3. ✅ Navigate to `/admin/users`
4. ✅ Navigate to `/assessments`
5. ✅ Create new assessment
6. ✅ View assessment details
7. ✅ Test logout

---

## Environment Variables

**Required in `.env`:**
```bash
VITE_API_BASE_URL=http://localhost:8000  # Backend API URL
VITE_APP_NAME=Nudj                       # Application name
VITE_DEFAULT_LANGUAGE=ar                  # Default language (ar/en)
```

---

## Language Support (i18n)

**Supported Languages:**
- 🇸🇦 Arabic (ar) - Default, RTL layout
- 🇬🇧 English (en) - LTR layout

**Language Switching:**
- Available in navbar/header
- Stored in localStorage
- Affects:
  - UI text
  - API `Accept-Language` header
  - Layout direction (RTL/LTR)
  - Date/number formatting

---

## Summary

**Total Frontend Routes:** 15
- Public: 4
- Protected: 11

**Total Backend API Endpoints:** 40+
- Auth: 12 endpoints
- Admin: 7 endpoints
- Assessments: 8 endpoints
- Organizations: 5 endpoints
- Delegations: 4 endpoints
- Framework: 2 endpoints
- Dashboards: 3 endpoints
- Comments: 4 endpoints
- Notifications: 4 endpoints

**Role-Based Access Control:** 4 roles with hierarchical permissions

**Frontend Status:** ✅ All import issues resolved, ready for testing

---

## Quick Reference

**Frontend:** http://localhost:5174
**Backend API:** http://localhost:8000
**API Docs:** http://localhost:8000/docs
**Test Login:** admin@nudj.sa / Nudj@2026Admin

**Key Features:**
- 🔐 JWT-based authentication with refresh tokens
- 🌐 Bilingual (Arabic/English) with RTL support
- 📊 Role-based dashboards
- 📝 HR maturity assessments (9 domains)
- 👥 User management with invitations
- 🔍 Audit logging
- 📄 PDF report generation
- 💬 Comments/collaboration on responses
- 🔔 Real-time notifications

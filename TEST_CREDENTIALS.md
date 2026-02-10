# Nudj Platform - Test Credentials & Configuration

## 🌐 Access URLs

- **Frontend**: http://localhost:5175/login
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs (when DEBUG=True)

---

## 👥 Test User Accounts

All test users have the password: **`Test@2026`**

### Super Admin (Platform Administrator)
- **Email**: `admin@nudj.sa`
- **Password**: `Nudj@2026Admin`
- **Name**: Super Admin
- **Organization**: N/A (Platform-wide access)
- **Permissions**: Full platform access
- **Use Case**: Platform configuration, user management, system monitoring

### Analyst (HR Maturity Consultant)
- **Email**: `analyst@nudj.sa`
- **Password**: `Test@2026`
- **Name**: HR Analyst (محلل الموارد البشرية)
- **Organization**: N/A (Cross-organization access)
- **Permissions**: View/edit assessments, generate reports
- **Use Case**: Review assessments, provide recommendations, analyze maturity scores

### Client Admin #1 (Organization Administrator)
- **Email**: `admin@advtech.sa`
- **Password**: `Test@2026`
- **Name**: Ahmed AlSaeed (أحمد السعيد)
- **Organization**: Advanced Technology Company
- **Permissions**: Manage organization users, view/edit assessments, view reports
- **Use Case**: Initiate assessments, delegate to assessors, view organization progress

### Client Admin #2 (Organization Administrator)
- **Email**: `admin@hrexcellence.sa`
- **Password**: `Test@2026`
- **Name**: Fatima AlOtaibi (فاطمة العتيبي)
- **Organization**: Excellence HR Solutions
- **Permissions**: Manage organization users, view/edit assessments, view reports
- **Use Case**: Initiate assessments, delegate to assessors, view organization progress

### Assessor #1 (Domain Specialist)
- **Email**: `assessor1@advtech.sa`
- **Password**: `Test@2026`
- **Name**: Sarah AlMohammadi (سارة المحمدي)
- **Organization**: Advanced Technology Company
- **Permissions**: Fill assigned assessment domains
- **Use Case**: Complete assigned assessment sections (e.g., Recruitment, Training domains)

### Assessor #2 (Domain Specialist)
- **Email**: `assessor@hrexcellence.sa`
- **Password**: `Test@2026`
- **Name**: Khaled AlShammari (خالد الشمري)
- **Organization**: Excellence HR Solutions
- **Permissions**: Fill assigned assessment domains
- **Use Case**: Complete assigned assessment sections

---

## 🏢 Test Organizations

### 1. Advanced Technology Company
- **Name (AR)**: شركة التقنية المتقدمة
- **Name (EN)**: Advanced Technology Company
- **CR Number**: 1010123456
- **Sector**: Information Technology
- **Size**: Medium
- **Region**: Riyadh

### 2. Excellence HR Solutions
- **Name (AR)**: مؤسسة الموارد البشرية المتميزة
- **Name (EN)**: Excellence HR Solutions
- **CR Number**: 1010234567
- **Sector**: Professional Services
- **Size**: Small
- **Region**: Jeddah

### 3. Industrial Innovation Group
- **Name (AR)**: مجموعة الابتكار الصناعي
- **Name (EN)**: Industrial Innovation Group
- **CR Number**: 1010345678
- **Sector**: Manufacturing
- **Size**: Enterprise
- **Region**: Dammam

---

## 📧 Email Configuration (SMTP)

Current configuration in `.env`:

```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=noreply@thrwty.com
EMAIL_HOST_PASSWORD=%d52WM\0jx8}
```

### Email Features
- ✅ Welcome emails on registration
- ✅ Password reset emails
- ✅ Assessment delegation notifications
- ✅ Assessment completion notifications
- ✅ Report ready notifications

### Testing Email Notifications

To test email notifications, trigger any of these actions:
1. **Password Reset**: Use "Forgot Password" on login page
2. **Invitation**: Super Admin invites a new user
3. **Assessment Delegation**: Client Admin delegates assessment to Assessor
4. **Assessment Completion**: Complete an assessment (triggers notification to Client Admin and Analyst)

---

## 🔔 In-App Notifications

Each test user has 2 pre-created notifications:
- Welcome notification
- Role-specific action notification

### API Endpoints for Notifications

```bash
# Get all notifications for current user
curl -X GET "http://localhost:8000/api/notifications/?limit=20" \
  -H "Authorization: Bearer <access_token>"

# Get unread count
curl -X GET "http://localhost:8000/api/notifications/unread-count" \
  -H "Authorization: Bearer <access_token>"

# Mark notification as read
curl -X PATCH "http://localhost:8000/api/notifications/{notification_id}/read" \
  -H "Authorization: Bearer <access_token>"
```

---

## 🔐 Authentication Testing

### Login Request Example

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@nudj.sa",
    "password": "Test@2026",
    "remember_me": false
  }'
```

### Response (Success)

```json
{
  "requires_mfa": false,
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": "984a20e0-73b5-46df-b055-d0b564d49cc3",
    "email": "analyst@nudj.sa",
    "name_ar": "محلل الموارد البشرية",
    "name_en": "HR Analyst",
    "role": "analyst",
    "organization_id": null,
    "mfa_enabled": false,
    "permissions": [
      "users:read",
      "orgs:read",
      "assessments:read",
      "assessments:write",
      "reports:read",
      "reports:write"
    ]
  }
}
```

---

## 🧪 Test Scenarios by Role

### Super Admin
1. Login with `admin@nudj.sa`
2. View all organizations in platform
3. Create/edit users across organizations
4. View system-wide analytics
5. Configure SSO settings

### Analyst
1. Login with `analyst@nudj.sa`
2. View pending assessments
3. Review assessment responses
4. Generate maturity reports
5. Access cross-organization data

### Client Admin
1. Login with `admin@advtech.sa` or `admin@hrexcellence.sa`
2. Initiate new assessment for organization
3. Invite assessors to organization
4. Delegate assessment domains to assessors
5. View organization's maturity score progress
6. Download assessment reports

### Assessor
1. Login with `assessor1@advtech.sa` or `assessor@hrexcellence.sa`
2. View assigned assessment domains
3. Fill assessment responses for assigned domains
4. Add comments on assessment elements
5. Submit completed domains

---

## 🚀 Quick Start Testing Workflow

1. **Start Backend**: `venv/Scripts/python.exe -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload`
2. **Start Frontend**: `cd src/frontend && npm run dev`
3. **Login as Super Admin**: `admin@nudj.sa` / `Nudj@2026Admin`
4. **Create Test Assessment**: Navigate to Assessments → New Assessment
5. **Login as Client Admin**: `admin@advtech.sa` / `Test@2026`
6. **Delegate to Assessor**: Navigate to Assessment → Delegate Domains
7. **Login as Assessor**: `assessor1@advtech.sa` / `Test@2026`
8. **Fill Assessment**: Complete assigned domains
9. **Check Notifications**: All users will receive in-app and email notifications

---

## 📝 Database Access

**Connection String** (from `.env`):
```
postgresql://nudj_user:nudj_password@localhost:5432/nudj_db
```

**psql Command**:
```bash
psql -h localhost -p 5432 -U nudj_user -d nudj_db
```

**Useful Queries**:
```sql
-- View all users
SELECT email, role, name_en, organization_id, is_active FROM users;

-- View all notifications
SELECT u.email, n.title, n.type, n.is_read, n.created_at
FROM notifications n
JOIN users u ON n.user_id = u.id
ORDER BY n.created_at DESC;

-- View organizations with user counts
SELECT o.name_en, COUNT(u.id) as user_count
FROM organizations o
LEFT JOIN users u ON u.organization_id = o.id
GROUP BY o.id, o.name_en;
```

---

## 🔧 Troubleshooting

### Issue: "Rate Limit Exceeded" (429 Error)
**Solution**: Rate limiting is disabled in development mode. If you see this error, ensure `.env` has `DEBUG=True`

### Issue: "CORS Policy Blocked"
**Solution**: Backend `config.py` includes ports 5174 and 5175 in CORS_ORIGINS. Ensure frontend is running on one of these ports.

### Issue: Email Notifications Not Sending
**Solution**: Verify SMTP credentials in `.env` are correct. Check backend logs for email sending errors.

### Issue: MFA Required for Super Admin
**Solution**: MFA is disabled for the super admin account. If enabled, run:
```sql
UPDATE users SET mfa_enabled = false WHERE email = 'admin@nudj.sa';
```

---

**Last Updated**: 2026-02-09
**Environment**: Development (POC)

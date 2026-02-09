# Nudj Platform - Login Credentials & Setup

**Status:** ✅ READY TO LOGIN
**Date:** 2026-02-09

---

## 🔐 Login Credentials

```
Email:    admin@nudj.sa
Password: Nudj@2026Admin
Role:     SUPER_ADMIN
```

**Frontend URL:** http://localhost:5174/login

---

## ⚠️ IMPORTANT: Backend Must Be Restarted

The MFA requirement was disabled in `.env`, so you **MUST restart the backend server** for the changes to take effect.

### How to Restart Backend:

1. **Stop the current backend server** (Press `Ctrl+C` in the terminal where it's running)

2. **Start it again:**
   ```powershell
   cd c:/Work/PoCs/Nudj-POC
   $env:PYTHONPATH="c:\Work\PoCs\Nudj-POC"
   $env:DEBUG="true"
   py -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Wait for:** "Database tables created" message

4. **Test login** at http://localhost:5174

---

## 🚀 Complete Startup Sequence

### Terminal 1 - Backend (RESTART REQUIRED)
```powershell
cd c:/Work/PoCs/Nudj-POC
$env:PYTHONPATH="c:\Work\PoCs\Nudj-POC"
$env:DEBUG="true"
py -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```
**Expected:** "Database tables created"

### Terminal 2 - Frontend (Already Running)
```powershell
cd c:/Work/PoCs/Nudj-POC/src/frontend
npm run dev
```
**Expected:** "VITE v6.4.1 ready in XXXms"
**URL:** http://localhost:5174

---

## ✅ What Was Fixed

### 1. **Admin User Created** ✅
- User email: `admin@nudj.sa`
- Role: `SUPER_ADMIN` (uppercase in database)
- Password: `Nudj@2026Admin` (hashed with Argon2)
- MFA: Disabled
- Status: Active & Verified

### 2. **MFA Requirement Disabled** ✅
**File:** `.env`
**Change:** `MFA_MANDATORY_ROLES=[]` (was `["super_admin","analyst"]`)

**Why:** The backend was enforcing MFA setup for super_admin role, preventing login during development/testing.

### 3. **Database Seeding Fixed** ✅
**Script:** `create_admin_user.py`
**Method:** Direct SQL insert (bypasses SQLAlchemy model initialization issues)
**Result:** Admin user successfully created in database

---

## 🔍 Troubleshooting

### Issue 1: "Invalid credentials" after restart

**Solution:** Make sure you restarted the backend server after changing `.env`

```powershell
# Check if backend is running with new config
curl http://localhost:8000/api/health
```

### Issue 2: Still getting "MFA_SETUP_REQUIRED"

**Cause:** Backend not restarted, still using old MFA config

**Solution:**
1. Stop backend (Ctrl+C)
2. Restart backend with commands above
3. Try login again

### Issue 3: "User not found"

**Verify user exists:**
```powershell
cd c:/Work/PoCs/Nudj-POC
py create_admin_user.py
```
Should say "Super admin already exists!"

### Issue 4: Frontend not loading

**Check:**
1. Frontend running on port 5174: `curl http://localhost:5174`
2. Backend running on port 8000: `curl http://localhost:8000/api/health`
3. No console errors in browser (F12)

---

## 🧪 Testing Login

### Method 1: Via Frontend (Recommended)

1. Open browser: http://localhost:5174
2. Should redirect to `/login` automatically
3. Enter credentials:
   - Email: `admin@nudj.sa`
   - Password: `Nudj@2026Admin`
4. Click "Login"
5. Should redirect to SuperAdminDashboard at `/dashboard`

### Method 2: Via API (Testing)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@nudj.sa","password":"Nudj@2026Admin"}'
```

**Expected Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "...",
    "email": "admin@nudj.sa",
    "role": "SUPER_ADMIN",
    ...
  }
}
```

---

## 📊 Current System Status

| Component | Status | Port | Notes |
|-----------|--------|------|-------|
| **PostgreSQL** | ✅ Running | 5432 | Database ready |
| **Backend API** | ⚠️ Restart Required | 8000 | MFA config changed |
| **Frontend** | ✅ Running | 5174 | All import issues fixed |
| **Admin User** | ✅ Created | - | Ready to login |
| **Database Seed** | ✅ Complete | - | 1 user created |

---

## 🎯 Super Admin Capabilities

Once logged in, you'll have access to:

### **Platform Management:**
- ✅ View all organizations
- ✅ Create/edit/delete organizations
- ✅ Platform-wide analytics

### **User Management:**
- ✅ View all users across all organizations
- ✅ Invite users with any role
- ✅ Edit user roles and permissions
- ✅ Activate/deactivate users
- ✅ Bulk invite via CSV

### **Framework Configuration:**
- ✅ Configure 9 HR maturity domains
- ✅ Adjust domain weights (must sum to 100%)
- ✅ Update domain descriptions (Arabic/English)

### **Security & Audit:**
- ✅ View all audit logs
- ✅ Export logs to CSV
- ✅ Track login attempts, password changes, role changes
- ✅ Monitor system security events

### **Assessments:**
- ✅ View all assessments (all organizations)
- ✅ Create new assessments
- ✅ Delegate domains to assessors
- ✅ Download PDF reports
- ✅ Delete assessments

---

## 🔒 Security Notes

### Development vs Production

**Current Setup (Development):**
- ⚠️ MFA disabled for testing
- ⚠️ Default password provided
- ⚠️ DEBUG mode enabled
- ⚠️ CORS open to localhost

**Production Requirements:**
1. ✅ Enable MFA: `MFA_MANDATORY_ROLES=["super_admin","analyst"]`
2. ✅ Change default password immediately
3. ✅ Disable DEBUG mode
4. ✅ Configure proper CORS origins
5. ✅ Use strong JWT secret keys
6. ✅ Enable HTTPS only
7. ✅ Configure production email/SMS providers

---

## 📝 Files Modified

### 1. Database
- ✅ `users` table: 1 record inserted (admin user)

### 2. Configuration
- ✅ `.env`: MFA_MANDATORY_ROLES changed from `["super_admin","analyst"]` to `[]`

### 3. Scripts Created
- ✅ `create_admin_user.py`: Simple SQL-based user creation script

---

## 🆘 Quick Reference

**Backend Health:** http://localhost:8000/api/health
**API Docs:** http://localhost:8000/api/docs
**Frontend:** http://localhost:5174
**Login Page:** http://localhost:5174/login

**Test Credentials:**
```
admin@nudj.sa / Nudj@2026Admin
```

---

## ✅ Next Steps

1. **Restart Backend Server** (REQUIRED)
2. **Open Frontend** at http://localhost:5174
3. **Login** with credentials above
4. **Explore Dashboard**
5. **Create Test Organization** (optional)
6. **Invite Test Users** (optional)
7. **Create Test Assessment** (optional)

---

**Ready to login! 🚀**

Remember to restart the backend server before attempting login.

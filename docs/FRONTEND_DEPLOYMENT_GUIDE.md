# Nudj Platform - Frontend Deployment Guide

**Status:** ⚠️ **Requires Node.js Installation**
**Date:** 2026-02-09

---

## 🚨 Prerequisites

### Required Software

| Software | Version | Status | Download Link |
|----------|---------|--------|---------------|
| **Node.js** | v20.x LTS | ❌ **NOT INSTALLED** | https://nodejs.org/en/download/ |
| **npm** | v10.x | ❌ (comes with Node.js) | - |
| **Backend API** | Running | ✅ http://localhost:8000 | Already deployed |

---

## 📋 Step-by-Step Deployment

### Step 1: Install Node.js

1. **Download Node.js LTS (v20.x)**
   - Visit: https://nodejs.org/en/download/
   - Download: Windows Installer (.msi) 64-bit
   - Recommended: v20.11.0 LTS or later

2. **Run the Installer**
   - Double-click the downloaded `.msi` file
   - Follow the installation wizard
   - ✅ Check "Automatically install necessary tools" (includes build tools)
   - Complete the installation

3. **Verify Installation**
   Open a **new** command prompt or PowerShell window:
   ```powershell
   node --version
   # Should output: v20.x.x

   npm --version
   # Should output: v10.x.x
   ```

   **Important:** You MUST open a new terminal after installation for PATH changes to take effect.

---

### Step 2: Install Frontend Dependencies

```powershell
# Navigate to frontend directory
cd c:\Work\PoCs\Nudj-POC\src\frontend

# Install all npm packages (this will take 2-5 minutes)
npm install
```

**Expected Output:**
```
added 1247 packages, and audited 1248 packages in 3m

found 0 vulnerabilities
```

---

### Step 3: Create Missing API Client

The frontend references `@/shared/lib/api-client` which doesn't exist yet. Create it:

**File:** `src/frontend/src/shared/lib/api-client.ts`

```typescript
import axios, { AxiosInstance, InternalAxesError, AxiosResponse } from 'axios';

// API base URL - in development, Vite proxy handles /api -> http://localhost:8000/api
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for session management
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage (managed by auth store)
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add language header for i18n
    const language = localStorage.getItem('language') || 'ar';
    config.headers['Accept-Language'] = language;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: any) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('accessToken', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle other errors
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.error?.message_en ||
                          error.response.data?.detail ||
                          'An error occurred';
      console.error('API Error:', errorMessage);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

**Create the directory first:**
```powershell
mkdir c:\Work\PoCs\Nudj-POC\src\frontend\src\shared\lib
```

---

### Step 4: Create Environment Configuration (Optional)

Create `.env` file in `src/frontend/`:

```properties
# API Configuration
VITE_API_BASE_URL=/api

# Environment
VITE_ENV=development

# Feature Flags
VITE_ENABLE_SSO=true
VITE_ENABLE_MFA=true
```

**Note:** The Vite config already has a proxy setup, so `/api` will automatically forward to `http://localhost:8000/api`

---

### Step 5: Start Development Server

```powershell
# From frontend directory
cd c:\Work\PoCs\Nudj-POC\src\frontend

# Start Vite dev server
npm run dev
```

**Expected Output:**
```
  VITE v6.0.11  ready in 3247 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 🌐 Access the Application

Once the server starts, open your browser:

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

---

## 🔗 API Connection Verification

The Vite config includes a proxy that forwards all `/api/*` requests to the backend:

```typescript
// vite.config.ts
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

This means:
- Frontend calls: `fetch('/api/auth/login')`
- Vite proxies to: `http://localhost:8000/api/auth/login`
- No CORS issues in development ✅

---

## 🧪 Testing User Experience

### 1. Test API Connection

Open browser console (F12) and run:
```javascript
fetch('/api/health')
  .then(r => r.json())
  .then(console.log)
// Should output: {status: "healthy", version: "1.0.0", ...}
```

### 2. Test Login Flow

Since no super admin user exists yet, you'll need to create one first. See **Step 6** below.

---

## 🔐 Step 6: Create Super Admin User (Required)

The database is empty - you need to create the first super admin user.

### Option A: Direct Database Insert

```sql
-- Connect to PostgreSQL
docker exec -it nudj-postgres psql -U postgres -d nudj

-- Create super admin user
INSERT INTO users (
  id,
  email,
  password_hash, -- Will set password manually via API
  name_ar,
  name_en,
  role,
  is_active,
  is_verified,
  mfa_enabled,
  failed_login_attempts,
  created_at,
  updated_at
) VALUES (
  gen_random_uuid(),
  'admin@nudj.sa',
  '$argon2id$v=19$m=65536,t=3,p=4$...',  -- Placeholder, use reset password
  'المسؤول الرئيسي',
  'Super Admin',
  'SUPER_ADMIN',
  true,
  true,
  false,
  0,
  NOW(),
  NOW()
);
```

### Option B: Use Backend Seed Script (Recommended)

Create a seed script to initialize the database:

**File:** `src/backend/seed.py`

```python
"""
Seed script to create initial super admin user.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.backend.database import get_async_session
from src.backend.app.auth.models import User, Role
from src.backend.app.auth.password_service import PasswordService
from src.backend.config import settings
import uuid

async def create_super_admin():
    """Create the first super admin user."""
    from src.backend.database import get_engine, get_async_session

    engine = get_engine()
    async with get_async_session(engine) as session:
        # Check if super admin already exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.role == Role.SUPER_ADMIN).limit(1)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"✅ Super admin already exists: {existing.email}")
            return

        # Create super admin
        password_service = PasswordService()
        password_hash = password_service.hash_password("Nudj@2026Admin")

        admin = User(
            id=uuid.uuid4(),
            email="admin@nudj.sa",
            password_hash=password_hash,
            name_ar="المسؤول الرئيسي",
            name_en="Super Admin",
            role=Role.SUPER_ADMIN,
            is_active=True,
            is_verified=True,
            mfa_enabled=False,
            failed_login_attempts=0,
        )

        session.add(admin)
        await session.commit()

        print("✅ Super admin created successfully!")
        print(f"   Email: admin@nudj.sa")
        print(f"   Password: Nudj@2026Admin")
        print(f"   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN")

if __name__ == "__main__":
    asyncio.run(create_super_admin())
```

**Run the seed script:**
```powershell
$env:PYTHONPATH="c:\Work\PoCs\Nudj-POC"
py src\backend\seed.py
```

---

## 🎯 Complete User Journey Test

### Test Flow:

1. **Start Backend** (if not running):
   ```powershell
   $env:PYTHONPATH="c:\Work\PoCs\Nudj-POC"
   $env:DEBUG="true"
   py -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend**:
   ```powershell
   cd c:\Work\PoCs\Nudj-POC\src\frontend
   npm run dev
   ```

3. **Open Browser**: http://localhost:5173

4. **Login as Super Admin**:
   - Email: `admin@nudj.sa`
   - Password: `Nudj@2026Admin`

5. **Expected Journey**:
   - Login page → Authentication
   - Redirect to Super Admin Dashboard
   - View Portfolio Dashboard with metrics
   - Navigate to Organizations → Create new organization
   - Navigate to Admin → Users → Invite users
   - Test full assessment flow

---

## 🐛 Troubleshooting

### Issue: `npm: command not found`
**Solution:** Install Node.js and restart your terminal

### Issue: `Cannot find module '@/shared/lib/api-client'`
**Solution:** Create the `api-client.ts` file as shown in Step 3

### Issue: Frontend shows CORS errors
**Solution:** Verify backend is running on port 8000 and Vite proxy is configured

### Issue: Login fails with 404
**Solution:** Create super admin user first (Step 6)

### Issue: `ENOENT: no such file or directory`
**Solution:** Run `npm install` to install dependencies

---

## 📊 Current Status Summary

| Component | Status | Details |
|-----------|--------|---------|
| Backend API | ✅ Running | http://localhost:8000 |
| Database | ✅ Ready | PostgreSQL with full schema |
| Frontend Code | ✅ Complete | React + Vite + shadcn/ui |
| Dependencies | ❌ **Missing** | **npm install** required |
| API Client | ❌ **Missing** | Needs to be created |
| Super Admin | ❌ **Missing** | Needs to be seeded |
| Node.js | ❌ **NOT INSTALLED** | **BLOCKER** |

---

## ⏭️ Next Steps

1. ✅ **Install Node.js v20.x LTS**
2. ✅ **Run `npm install` in frontend directory**
3. ✅ **Create `api-client.ts` file**
4. ✅ **Create super admin seed script and run it**
5. ✅ **Start frontend dev server**
6. ✅ **Test complete user journey**
7. ✅ **Document any issues found during testing**

---

**Generated:** 2026-02-09
**Platform:** Nudj (نُضْج) - HR Maturity Assessment Platform
**Version:** V1.0 POC

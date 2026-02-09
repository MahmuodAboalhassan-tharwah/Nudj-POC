# Nudj Platform - Quick Start Guide

**Status:** ✅ Ready to Start
**Date:** 2026-02-09

---

## ✅ Prerequisites Completed

- ✅ Node.js installed (v24.13.0)
- ✅ npm installed (v11.6.2)
- ✅ Frontend dependencies installed (689 packages)
- ✅ Backend code ready
- ✅ API client created
- ✅ Super admin seed script ready

---

## 🚀 Start the Platform (4 Steps)

### Step 1: Start Docker Desktop

1. **Open Docker Desktop** from Windows Start Menu
2. **Wait for Docker to be running** (Docker icon in system tray should be green)
3. **Verify:**
   ```powershell
   docker ps
   # Should NOT show error
   ```

---

### Step 2: Start Backend Services (Terminal 1)

```powershell
# Navigate to project
cd c:\Work\PoCs\Nudj-POC

# Start Docker containers
docker-compose up -d postgres redis

# Verify containers are running
docker ps

# Set environment variables
$env:PYTHONPATH="c:\Work\PoCs\Nudj-POC"
$env:DEBUG="true"

# Start backend server
py -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait for:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
Database tables created
```

**Test backend:**
```powershell
# In another terminal
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"1.0.0",...}
```

---

### Step 3: Create Super Admin (Terminal 2)

**IMPORTANT:** Only run this ONCE (first time only)

```powershell
cd c:\Work\PoCs\Nudj-POC

# Run seed script
py src\backend\seed.py
```

**Expected Output:**
```
[SUCCESS] Super admin created successfully!
Email:    admin@nudj.sa
Password: Nudj@2026Admin
```

**Note:** If you see "Super admin already exists", that's fine - skip this step.

---

### Step 4: Start Frontend (Terminal 2 or 3)

```powershell
cd c:\Work\PoCs\Nudj-POC\src\frontend

# Start Vite dev server
npm run dev
```

**Wait for:**
```
VITE v6.0.11  ready in 2347 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## 🌐 Access the Application

1. **Open Browser:** http://localhost:5173

2. **Login Credentials:**
   - Email: `admin@nudj.sa`
   - Password: `Nudj@2026Admin`

3. **After Login:**
   - You should see the Super Admin Dashboard
   - Portfolio metrics and navigation menu

---

## 🧪 Test User Journey

### 1. Dashboard
- ✅ Portfolio overview with metrics
- ✅ Charts and statistics
- ✅ Navigation sidebar

### 2. Organizations
- Navigate to: **Admin → Organizations**
- Click **"Create Organization"**
- Fill in details:
  - Name (Arabic): شركة تجريبية
  - Name (English): Test Company
  - CR Number: 1234567890
  - Sector: Technology
  - Size: 51-200
  - Region: Riyadh
- **Save** and verify it appears in the list

### 3. User Management
- Navigate to: **Admin → Users**
- Click **"Invite User"**
- Fill in invitation form:
  - Email: test@example.com
  - Role: Client Admin
  - Organization: Select the one you just created
- **Send Invitation**
- Verify invitation sent successfully

### 4. Assessment Creation
- Navigate to: **Assessments**
- Click **"Create Assessment"**
- Select:
  - Organization
  - Domains (HR Strategy, Talent Management, etc.)
  - Deadline
- **Create** and verify it appears

### 5. Assessment Details
- Click on the created assessment
- Verify:
  - Domain tabs visible
  - Questions loaded
  - Evidence upload working
  - Comments functional

### 6. API Integration Test
- Open browser console (F12)
- Check Network tab for API calls
- Verify:
  - API calls go to `/api/*`
  - Authorization headers present
  - Responses are 200 OK

---

## 🛑 Stopping Services

```powershell
# Stop Frontend (Ctrl+C in terminal 2/3)

# Stop Backend (Ctrl+C in terminal 1)

# Stop Docker containers
docker-compose down
```

---

## 🐛 Troubleshooting

### Issue: Docker not found
**Solution:** Start Docker Desktop from Windows Start Menu

### Issue: Backend shows database connection error
**Solution:** Ensure Docker containers are running:
```powershell
docker ps | grep -E "(postgres|redis)"
```

### Issue: Frontend shows CORS error
**Solution:**
1. Verify backend is running on port 8000
2. Check Vite config has proxy setup (it does)
3. Restart both servers

### Issue: Login fails
**Solution:**
1. Check backend logs for errors
2. Verify super admin was created:
   ```powershell
   py src\backend\seed.py
   ```
3. Check browser console for API errors

### Issue: npm install fails
**Solution:**
```powershell
cd src\frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port 8000 already in use
**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

---

## 📊 Service URLs Reference

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Main application UI |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs (Swagger)** | http://localhost:8000/api/docs | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8000/api/redoc | Alternative API docs |
| **PostgreSQL** | localhost:5432 | Database (internal) |
| **Redis** | localhost:6379 | Cache (internal) |

---

## 📁 Project Structure Quick Reference

```
Nudj-POC/
├── src/
│   ├── backend/          # FastAPI backend
│   │   ├── main.py       # App entry point
│   │   ├── seed.py       # Super admin creation
│   │   └── app/          # Feature modules
│   └── frontend/         # React + Vite frontend
│       ├── src/
│       │   ├── features/ # Feature modules
│       │   └── shared/   # Shared components
│       └── package.json
├── docs/                 # Documentation
├── .env                  # Environment variables
└── docker-compose.yml    # Docker services config
```

---

## ⏭️ Next Steps After Testing

1. **Document Issues Found**
   - Create a list of bugs or missing features
   - Note any UI/UX improvements

2. **Customize for Your Needs**
   - Update organization types
   - Add assessment domains
   - Configure framework weights

3. **Plan V2 Features**
   - Benchmark Data Warehouse
   - AI HR Maturity Coach
   - Industry Insights

---

## 🤝 Support

- **Backend Issues:** Check [V1_DEPLOYMENT_SUCCESS.md](docs/V1_DEPLOYMENT_SUCCESS.md)
- **Frontend Issues:** Check [FRONTEND_DEPLOYMENT_GUIDE.md](docs/FRONTEND_DEPLOYMENT_GUIDE.md)
- **General Status:** Check [CURRENT_STATUS_SUMMARY.md](docs/CURRENT_STATUS_SUMMARY.md)

---

**Ready to start!** 🚀

**Estimated time to full deployment:** 5-10 minutes

---

**Generated:** 2026-02-09
**Platform:** Nudj (نُضْج) - HR Maturity Assessment Platform
**Version:** V1.0 POC

# 🚀 START HERE - Nudj Platform Quick Start

**Status:** ✅ All dependencies installed - Ready to start!

---

## ⚠️ IMPORTANT: Start Order Matters!

You **MUST** start services in this exact order:

1. **Backend first** (creates database tables)
2. **Seed script** (creates super admin)
3. **Frontend** (connects to backend)

---

## 🐛 Two Issues Fixed

### ✅ Issue 1: PowerShell Execution Policy - FIXED

**Solution:** Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Or use CMD instead:**
```cmd
cmd
cd c:\Work\PoCs\Nudj-POC\src\frontend
npm run dev
```

### ✅ Issue 2: Missing utils.ts - FIXED

Created [src/frontend/src/lib/utils.ts](src/frontend/src/lib/utils.ts)

---

## 🚀 Step-by-Step Startup (15 minutes)

### Step 1: Verify Docker is Running

```powershell
docker ps
```

If you get an error, **start Docker Desktop** and wait until it's fully running.

Then start containers:
```powershell
cd c:\Work\PoCs\Nudj-POC
docker-compose up -d postgres redis
```

Verify:
```powershell
docker ps | findstr postgres
docker ps | findstr redis
```

---

### Step 2: Start Backend Server (Terminal 1)

**IMPORTANT:** Keep this terminal open!

```powershell
cd c:\Work\PoCs\Nudj-POC

# Set environment variables
$env:PYTHONPATH="c:\Work\PoCs\Nudj-POC"
$env:DEBUG="true"

# Start backend
py -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait for this message:**
```
INFO:     Application startup complete.
Database tables created
```

**Test backend is working:**
Open browser to http://localhost:8000/api/health
Should show: `{"status":"healthy"}`

**Leave this terminal running! Do NOT close it!**

---

### Step 3: Create Super Admin (New Terminal 2)

**IMPORTANT:** Wait until backend from Step 2 shows "Database tables created"

```powershell
cd c:\Work\PoCs\Nudj-POC

# Run seed script
py src\backend\seed.py
```

**Expected output:**
```
[SUCCESS] Super admin created successfully!
Email:    admin@nudj.sa
Password: Nudj@2026Admin
```

**If you see "Super admin already exists" - that's fine, skip to Step 4!**

---

### Step 4: Start Frontend (Terminal 2 or 3)

**Option A: Using PowerShell (after fixing execution policy)**
```powershell
cd c:\Work\PoCs\Nudj-POC\src\frontend
npm run dev
```

**Option B: Using CMD (no policy issue)**
```cmd
cmd
cd c:\Work\PoCs\Nudj-POC\src\frontend
npm run dev
```

**Wait for:**
```
VITE v6.0.11  ready in 2347 ms
➜  Local:   http://localhost:5173/
```

---

### Step 5: Open Application

**Open browser:** http://localhost:5173

**Login:**
- Email: `admin@nudj.sa`
- Password: `Nudj@2026Admin`

**You should see:**
- ✅ Super Admin Dashboard
- ✅ Portfolio metrics
- ✅ Navigation menu

---

## 🧪 Quick Test Checklist

Once logged in, verify:

- [ ] Dashboard loads with metrics
- [ ] Navigation menu works
- [ ] Can navigate to Admin → Organizations
- [ ] Can navigate to Admin → Users
- [ ] Can navigate to Assessments
- [ ] No console errors in browser (F12)

---

## 🐛 Troubleshooting

### Backend won't start

**Check 1:** Docker containers running?
```powershell
docker ps
```

**Check 2:** Port 8000 already in use?
```powershell
netstat -ano | findstr :8000
```

**Solution:** Kill the process or use a different port

### Seed script fails with "table not found"

**Cause:** Backend is not running
**Solution:** Start backend first (Step 2), then run seed script

### Frontend shows import errors

**Check:** Is [src/lib/utils.ts](src/frontend/src/lib/utils.ts) present?
**Solution:** Already created - restart frontend server

### npm command not working in PowerShell

**Solution 1:** Fix execution policy (see above)
**Solution 2:** Use CMD instead of PowerShell

### Frontend shows CORS errors

**Check 1:** Backend running on port 8000?
```powershell
curl http://localhost:8000/api/health
```

**Check 2:** Vite proxy configured? (Yes, already done)

**Solution:** Restart both backend and frontend

---

## 📊 Service Status Check

Run these commands to verify everything:

```powershell
# Docker containers
docker ps

# Backend health
curl http://localhost:8000/api/health

# Frontend (open in browser)
# http://localhost:5173
```

---

## 🛑 Stopping Everything

```powershell
# Stop Frontend (Ctrl+C in terminal)

# Stop Backend (Ctrl+C in terminal)

# Stop Docker containers
docker-compose down
```

---

## 📁 Quick Reference

| What | URL/Command | Terminal |
|------|-------------|----------|
| **Backend** | http://localhost:8000 | Terminal 1 (keep open) |
| **Frontend** | http://localhost:5173 | Terminal 2 (keep open) |
| **API Docs** | http://localhost:8000/api/docs | Browser |
| **Login** | admin@nudj.sa / Nudj@2026Admin | Frontend |

---

## ⚡ Even Quicker Start (After First Time)

Once you've done the full setup once, subsequent starts are simpler:

**Terminal 1:**
```powershell
cd c:\Work\PoCs\Nudj-POC
$env:PYTHONPATH="c:\Work\PoCs\Nudj-POC"; $env:DEBUG="true"
py -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (wait for backend to show "Application startup complete"):**
```cmd
cmd
cd c:\Work\PoCs\Nudj-POC\src\frontend
npm run dev
```

**Browser:** http://localhost:5173

---

## 🎯 Success Criteria

You know it's working when:

- ✅ Backend shows "Application startup complete"
- ✅ Frontend shows "VITE ready"
- ✅ Login page loads at http://localhost:5173
- ✅ Can login with admin@nudj.sa
- ✅ Dashboard displays after login
- ✅ No errors in browser console

---

## 🤝 Need Help?

If you encounter issues:

1. Check this troubleshooting section
2. Review [QUICK_START.md](QUICK_START.md) for detailed guide
3. Check [CURRENT_STATUS_SUMMARY.md](docs/CURRENT_STATUS_SUMMARY.md) for status

---

**Ready to start!** Follow Steps 1-5 above. 🚀

**Estimated time:** 5-10 minutes (first time), 2-3 minutes (subsequent times)

---

**Generated:** 2026-02-09
**Platform:** Nudj (نُضْج) - HR Maturity Assessment Platform
**Version:** V1.0 POC

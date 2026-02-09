# Nudj Platform - Start All Services
# Quick start script for development

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Nudj Platform - Starting Services" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check Docker
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "  [OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop manually and run this script again." -ForegroundColor Yellow
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Step 2: Start Docker Containers
Write-Host "`n[2/4] Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d postgres redis
Start-Sleep -Seconds 3

$postgres = docker ps --filter "name=postgres" --format "{{.Status}}"
$redis = docker ps --filter "name=redis" --format "{{.Status}}"

if ($postgres -and $redis) {
    Write-Host "  [OK] PostgreSQL: $postgres" -ForegroundColor Green
    Write-Host "  [OK] Redis: $redis" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Containers failed to start" -ForegroundColor Red
    exit 1
}

# Step 3: Check Backend
Write-Host "`n[3/4] Checking backend server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2
    Write-Host "  [OK] Backend is running: http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "  [INFO] Backend is not running yet" -ForegroundColor Yellow
    Write-Host "  You need to start it manually in a separate terminal:" -ForegroundColor Cyan
    Write-Host "    cd c:\Work\PoCs\Nudj-POC" -ForegroundColor Gray
    Write-Host "    `$env:PYTHONPATH='c:\Work\PoCs\Nudj-POC'; `$env:DEBUG='true'" -ForegroundColor Gray
    Write-Host "    py -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
}

# Step 4: Check Frontend
Write-Host "`n[4/4] Checking frontend server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 2
    Write-Host "  [OK] Frontend is running: http://localhost:5173" -ForegroundColor Green
} catch {
    Write-Host "  [INFO] Frontend is not running yet" -ForegroundColor Yellow
    Write-Host "  You need to start it manually in a separate terminal:" -ForegroundColor Cyan
    Write-Host "    cd c:\Work\PoCs\Nudj-POC\src\frontend" -ForegroundColor Gray
    Write-Host "    npm run dev" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Service Status Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker:    " -NoNewline; Write-Host "[RUNNING]" -ForegroundColor Green
Write-Host "Backend:   " -NoNewline; if ($response) { Write-Host "[RUNNING]" -ForegroundColor Green } else { Write-Host "[STOPPED]" -ForegroundColor Yellow }
Write-Host "Frontend:  " -NoNewline; Write-Host "[CHECK MANUALLY]" -ForegroundColor Yellow
Write-Host "`n========================================`n" -ForegroundColor Cyan

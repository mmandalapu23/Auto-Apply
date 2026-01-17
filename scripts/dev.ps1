# PowerShell development script for Windows users
# Usage: .\scripts\dev.ps1 [api|worker|migrate|all]

param(
    [string]$command = "all"
)

$env:PYTHONUNBUFFERED = 1

function Start-API {
    Write-Host "Starting FastAPI server..." -ForegroundColor Green
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Start-Worker {
    Write-Host "Starting Celery worker..." -ForegroundColor Green
    cd backend
    celery -A app.workers.celery_app worker --loglevel=info
}

function Run-Migrations {
    Write-Host "Running database migrations..." -ForegroundColor Green
    cd backend
    alembic upgrade head
}

switch ($command) {
    "api" { Start-API }
    "worker" { Start-Worker }
    "migrate" { Run-Migrations }
    "all" {
        Write-Host "Starting all services..." -ForegroundColor Cyan
        Write-Host "Make sure Docker containers (postgres, redis) are running!" -ForegroundColor Yellow
        $jobs = @()
        $jobs += Start-Job -ScriptBlock { & .\scripts\dev.ps1 migrate }
        $jobs += Start-Job -ScriptBlock { & .\scripts\dev.ps1 api }
        $jobs += Start-Job -ScriptBlock { & .\scripts\dev.ps1 worker }
        Get-Job | Wait-Job
    }
    default { Write-Host "Unknown command: $command" }
}

<#
.SYNOPSIS
    SENTINEL AI - Single-Command Launcher for API and Streamlit Dashboard
#>
[CmdletBinding()]
param(
    [ValidateSet("all", "dashboard", "api")]
    [string]$Mode = "dashboard"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         SENTINEL AI — LAUNCHING SYSTEM (Mode: $Mode)       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if ($Mode -eq "api") {
    Write-Host "[*] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
    python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
}
elseif ($Mode -eq "dashboard") {
    Write-Host "[*] Starting Streamlit Command Center on http://localhost:8501..." -ForegroundColor Green
    python -m streamlit run app.py --server.port 8501 --server.headless false
}
elseif ($Mode -eq "all") {
    Write-Host "[*] Starting FastAPI in background process..." -ForegroundColor Green
    Start-Process -FilePath "python" -ArgumentList "-m uvicorn server:app --host 127.0.0.1 --port 8000"
    Start-Sleep -Seconds 2
    Write-Host "[*] Starting Streamlit Command Center..." -ForegroundColor Green
    python -m streamlit run app.py --server.port 8501 --server.headless false
}

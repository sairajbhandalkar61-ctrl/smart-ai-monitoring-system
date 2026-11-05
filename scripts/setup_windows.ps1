<#
.SYNOPSIS
    SENTINEL AI - Automated Windows Environment Setup Script
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         SENTINEL AI — WINDOWS CPU SETUP INITIALIZER       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Run Doctor Diagnostic
Write-Host "[1/3] Running Hardware & Doctor Diagnostics..." -ForegroundColor Yellow
& powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\doctor.ps1"

# 2. Verify Python packages
Write-Host "`n[2/3] Verifying Core Dependencies..." -ForegroundColor Yellow
python -c "import torch, torchvision, cv2, fastapi, streamlit, pydantic; print('[+] All core dependencies verified successfully!')"

# 3. Initialize SQLite Database
Write-Host "`n[3/3] Initializing Database Schema..." -ForegroundColor Yellow
python -c "from sentinel.storage.database import init_db; init_db(); print('[+] Database initialized at data/sentinel.db')"

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE! Run .\scripts\run_sentinel.ps1 to launch." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

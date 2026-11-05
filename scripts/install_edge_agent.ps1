<#
.SYNOPSIS
    SENTINEL AI - Dell Latitude 3420 Edge Agent Installer
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       SENTINEL AI — DELL EDGE AGENT INSTALLER (Win 11)   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Run Doctor Diagnostic
Write-Host "[1/3] Checking Dell Hardware & Camera DirectShow..." -ForegroundColor Yellow
& powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\doctor.ps1"

# 2. Install edge requirements
Write-Host "`n[2/3] Verifying Edge Python Packages..." -ForegroundColor Yellow
pip install -r "$PSScriptRoot\..\requirements-edge-windows.txt"

# 3. Test camera and detector
Write-Host "`n[3/3] Probing Edge Vision Pipeline..." -ForegroundColor Yellow
python -c "import cv2, torch, torchvision; cap = cv2.VideoCapture(0, cv2.CAP_DSHOW); ret, frame = (cap.read() if cap.isOpened() else (False, None)); print(f'[+] Camera 0 probe: {ret}, Frame: {frame.shape if ret else None}'); cap.release()"

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "EDGE AGENT INSTALL COMPLETE! Run .\scripts\run_edge_agent.ps1" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

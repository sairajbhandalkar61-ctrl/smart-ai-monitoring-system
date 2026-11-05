<#
.SYNOPSIS
    SENTINEL AI - Dell Edge Agent Launcher
#>
[CmdletBinding()]
param(
    [string]$CloudUrl = "http://127.0.0.1:8000",
    [string]$DeviceId = "dell-edge-01",
    [string]$Token = "sentinel_edge_secure_token_2026"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       SENTINEL AI — DELL LATITUDE 3420 EDGE AGENT        " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[*] Target Cloud API: $CloudUrl" -ForegroundColor Green
Write-Host "[*] Device ID:       $DeviceId" -ForegroundColor Green
Write-Host "[*] Camera:          Integrated Webcam (Index 0, DirectShow)" -ForegroundColor Green
Write-Host "[*] Detector:        SSDLite320-MobileNetV3 (CPU)" -ForegroundColor Green
Write-Host "----------------------------------------------------------" -ForegroundColor Gray
Write-Host "[!] Press Ctrl+C at any time to halt edge monitoring." -ForegroundColor Yellow
Write-Host "----------------------------------------------------------" -ForegroundColor Gray

$env:CLOUD_API_URL = $CloudUrl
$env:EDGE_DEVICE_ID = $DeviceId
$env:EDGE_DEVICE_TOKEN = $Token

python -u sentinel\edge\agent.py

<#
.SYNOPSIS
    SENTINEL AI - Environment & Hardware Doctor Diagnostics
.DESCRIPTION
    Verifies CPU, RAM, camera presence, Python environment, and disk space.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         SENTINEL AI - SYSTEM DOCTOR & ENVIRONMENT CHECK   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. CPU & Memory
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$cs = Get-CimInstance Win32_ComputerSystem | Select-Object -First 1
$ramGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)

Write-Host "[+] CPU: $($cpu.Name) ($($cpu.NumberOfCores) Cores, $($cpu.NumberOfLogicalProcessors) Threads)" -ForegroundColor Green
Write-Host "[+] RAM: $ramGB GB physical memory available" -ForegroundColor Green

# 2. GPU
$gpus = Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }
Write-Host "[+] GPU(s): $($gpus -join ', ')" -ForegroundColor Green
if ($gpus -match "NVIDIA") {
    Write-Host "    [!] NVIDIA GPU detected." -ForegroundColor Yellow
} else {
    Write-Host "    [*] Pure CPU / Integrated iGPU detected. Enforcing CPU-first pipeline." -ForegroundColor Gray
}

# 3. Camera
$cameras = Get-PnpDevice -Class Camera, Image -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "OK" }
if ($cameras) {
    Write-Host "[+] Camera(s) Found:" -ForegroundColor Green
    foreach ($cam in $cameras) {
        Write-Host "    - $($cam.FriendlyName) (Status: $($cam.Status))" -ForegroundColor Gray
    }
} else {
    Write-Host "[!] No active camera detected via PnP." -ForegroundColor Red
}

# 4. Python Environment
$pyVer = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] Python: $pyVer" -ForegroundColor Green
} else {
    Write-Host "[!] Python command not found in PATH." -ForegroundColor Red
}

# 5. Disk Space
$disk = Get-PSDrive C
$freeGB = [math]::Round($disk.Free / 1GB, 2)
if ($freeGB -ge 10) {
    Write-Host "[+] Disk Space (C:): $freeGB GB free (Sufficient)" -ForegroundColor Green
} else {
    Write-Host "[!] Disk Space (C:): $freeGB GB free (Low disk space warning)" -ForegroundColor Yellow
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Doctor checks complete." -ForegroundColor Cyan

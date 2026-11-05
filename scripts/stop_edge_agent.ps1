<#
.SYNOPSIS
    SENTINEL AI - Cleanly Stops Any Running Edge Agent or Camera Processes
#>
[CmdletBinding()]
param()

Write-Host "[*] Finding and terminating running edge agent processes..." -ForegroundColor Yellow

$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*sentinel\edge\agent.py*" }
if ($procs) {
    foreach ($p in $procs) {
        Stop-Process -Id $p.ProcessId -Force
        Write-Host "[+] Terminated Process ID $($p.ProcessId)" -ForegroundColor Green
    }
} else {
    Write-Host "[*] No active edge agent processes found." -ForegroundColor Gray
}

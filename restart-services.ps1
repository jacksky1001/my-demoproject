# Restart backend and frontend services
param(
    [string]$HostAddress = "0.0.0.0",
    [int]$BackendPort = 8191,
    [int]$FrontendPort = 8188
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Vision Center - Restarting Services" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host ">>> Stopping services..." -ForegroundColor Yellow

$stopScript = Join-Path $ScriptDir "stop-services.ps1"
& $stopScript

Start-Sleep -Seconds 2
Write-Host ""
Write-Host ">>> Starting services..." -ForegroundColor Yellow

$startScript = Join-Path $ScriptDir "start-services.ps1"
& $startScript -HostAddress $HostAddress -BackendPort $BackendPort -FrontendPort $FrontendPort

# Start backend and frontend services
param(
    [string]$HostAddress = "0.0.0.0",
    [int]$BackendPort = 8191,
    [int]$FrontendPort = 8188
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "logs"
$LanIp = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and $_.PrefixOrigin -ne 'WellKnown' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Vision Center - Starting Services" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/2] Starting backend..." -ForegroundColor Yellow

$backendJob = Start-Job -Name "vision-backend" -ScriptBlock {
    param($dir, $logDir, $hostAddress, $backendPort)
    Set-Location $dir
    $logFile = Join-Path $logDir "backend.log"
    & python main.py --host=$hostAddress --port=$backendPort --no-reload 2>&1 | Out-File -FilePath $logFile -Append
} -ArgumentList $ScriptDir, $LogDir, $HostAddress, $BackendPort

Write-Host "  Backend Job ID: $($backendJob.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "[2/2] Starting frontend..." -ForegroundColor Yellow

$frontendJob = Start-Job -Name "vision-frontend" -ScriptBlock {
    param($dir, $logDir, $hostAddress, $frontendPort)
    $webDir = Join-Path $dir "web"
    Set-Location $webDir
    $logFile = Join-Path $logDir "frontend.log"
    & npm run dev -- --host $hostAddress --port $frontendPort 2>&1 | Out-File -FilePath $logFile -Append
} -ArgumentList $ScriptDir, $LogDir, $HostAddress, $FrontendPort

Write-Host "  Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $health = Invoke-RestMethod -Uri "http://localhost:$BackendPort/api/health" -Method Get -TimeoutSec 5
    Write-Host ""
    Write-Host "[Backend] OK - http://localhost:$BackendPort" -ForegroundColor Green
    Write-Host "  API Docs: http://localhost:$BackendPort/docs" -ForegroundColor Green
    if ($LanIp) {
        Write-Host "  LAN API: http://$LanIp`:$BackendPort/docs" -ForegroundColor Green
    }
} catch {
    Write-Host ""
    Write-Host "[Backend] Still starting, check http://localhost:$BackendPort" -ForegroundColor Magenta
}

Write-Host ""
Write-Host "[Frontend] http://localhost:$FrontendPort" -ForegroundColor Green
if ($LanIp) {
    Write-Host "[LAN Frontend] http://$LanIp`:$FrontendPort" -ForegroundColor Green
}
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Logs: $LogDir" -ForegroundColor Cyan
Write-Host "  Stop: .\stop-services.ps1" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

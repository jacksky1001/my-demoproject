# Stop backend and frontend services
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Vision Center - Stopping Services" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 1. 先通过 Job 名称停止
$backendJob = Get-Job -Name "vision-backend" -ErrorAction SilentlyContinue
$frontendJob = Get-Job -Name "vision-frontend" -ErrorAction SilentlyContinue

if ($backendJob) {
    Write-Host "[1/5] Stopping backend job..." -ForegroundColor Yellow
    Stop-Job -Name "vision-backend"
    Remove-Job -Name "vision-backend" -Force
    Write-Host "  Backend job removed" -ForegroundColor Green
} else {
    Write-Host "[1/5] No backend job" -ForegroundColor Green
}

if ($frontendJob) {
    Write-Host "[2/5] Stopping frontend job..." -ForegroundColor Yellow
    Stop-Job -Name "vision-frontend"
    Remove-Job -Name "vision-frontend" -Force
    Write-Host "  Frontend job removed" -ForegroundColor Green
} else {
    Write-Host "[2/5] No frontend job" -ForegroundColor Green
}

# 2. 通过端口查找并杀掉进程（修复了变量名问题）
Write-Host "[3/5] Cleaning backend processes by port..." -ForegroundColor Yellow
$killed = 0

# 查找监听 8181, 8182, 8190, 8191 的进程
$ports = @(8181, 8182, 8190, 8191)
foreach ($port in $ports) {
    $pids = netstat -ano 2>$null | Select-String ":$port " | Select-String "LISTENING" | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -Unique
    foreach ($procId in $pids) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "  Killed PID $procId on port $port" -ForegroundColor Green
            $killed++
        } catch {
            Write-Host "  Could not kill PID $procId on port $port" -ForegroundColor Gray
        }
    }
}

# 3. 通过进程名查找 Python
Write-Host "[4/5] Cleaning python processes..." -ForegroundColor Yellow
$pythonProcs = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*PrintServer-V1*" -or
    ($_.MainWindowTitle -eq "" -and $_.StartTime -lt (Get-Date).AddMinutes(-5))
}
if ($pythonProcs) {
    $pythonProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  Stopped $($pythonProcs.Count) python processes" -ForegroundColor Green
}

# 4. 通过进程名查找 node
Write-Host "[5/5] Cleaning node processes..." -ForegroundColor Yellow
$nodeProcs = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*PrintServer-V1*" -or
    ($_.StartTime -lt (Get-Date).AddMinutes(-5))
}
if ($nodeProcs) {
    $nodeProcs | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  Stopped $($nodeProcs.Count) node processes" -ForegroundColor Green
}

Write-Host ""
Write-Host "Total killed: $killed port-based, $($pythonProcs.Count) python, $($nodeProcs.Count) node" -ForegroundColor Cyan
Write-Host "All services stopped." -ForegroundColor Green

# 故障排除：多进程占用端口问题

## 问题描述

在开发过程中，多次出现多个 Python/Node 进程同时占用同一端口（8181、8182、8188 等）的情况，导致：

- 新服务无法启动
- 旧代码仍在运行，看不到最新修改
- API 404 错误（路由没有正确加载）

## 问题根源

### 1. **stop-services.ps1 的 bug**

```powershell
# 旧代码（错误）
foreach ($pid in $pids) {  # ❌ $pid 是 PowerShell 自动变量！
    Stop-Process -Id $pid ...
}
```

`$pid` 是 PowerShell 的自动变量，表示当前脚本进程 ID，导致永远不会杀掉目标进程。

### 2. **后台任务管理问题**

- 使用 `run_in_background` 启动的任务没有完善的跟踪机制
- 任务失败时仍可能残留子进程
- Uvicorn `--reload` 模式启动两个进程（监控+工作），停止时容易残留

### 3. **缺少单例检测**

- 启动时没有检查端口是否已被占用
- 没有防止重复启动的机制

## 已修复内容

### ✅ 1. stop-services.ps1 修复

- 修复了 `$pid` 变量名错误 → `$procId`
- 增加多端口检测（8181、8182、8190、8191）
- 增加进程路径过滤，避免误杀其他程序
- 更友好的错误处理

### ✅ 2. main.py 增强

- 启动前检查端口占用
- 警告用户
- 可选强制启动
- 添加 `--no-reload` 参数选项

### ✅ 3. 启动/停止脚本

- 使用 PowerShell Job 统一管理
- 可以通过 Job 名称停止
- 可以查看实时日志

## 如何使用

### 停止所有服务

```powershell
.\stop-services.ps1
```

### 重启服务（推荐）

```powershell
.\restart-services.ps1
```

### 手动启动

```powershell
# 后端（端口 8191）
python main.py --port=8191

# 前端（端口 8188）
cd web
npm run dev
```

### 查看运行中的 Job

```powershell
Get-Job
```

### 查看 Job 日志

```powershell
# 后端日志
Receive-Job -Name vision-backend -Keep

# 前端日志
Receive-Job -Name vision-frontend -Keep
```

### 清理所有残留（如果需要）

```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
```

## 当前端口分配

| 服务 | 端口 | 说明 |
|-----|------|------|
| 前端 | 8188 | Vite 开发服务器 |
| 后端 | 8191 | FastAPI (稳定) |
| 后端备用 | 8181, 8182 | 旧配置使用 |

## 预防措施

1. **永远使用脚本启动/停止**
   - 启动：`.\restart-services.ps1`
   - 停止：`.\stop-services.ps1`

2. **在 main.py 中看到端口占用警告时**
   - 先停止服务，再启动
   - 不要强制启动

3. **开发时注意**
   - 每次修改后检查是否有旧进程
   - 如果有异常，先运行停止脚本

4. **查看后端实际状态**
   访问 http://localhost:8191/docs 验证后端是否正常运行

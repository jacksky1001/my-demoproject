# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 项目概述

**项目名称**: 视力中心蓝牙数据汇聚系统 (Vision Center Bluetooth Data Aggregation System)

**项目性质**: 医疗设备数据集成与打印服务系统

**技术栈**:
- **后端**: Python 3.10+, FastAPI, SQLite
- **前端**: Vue 3 + TypeScript + Vite + Element Plus
- **硬件接口**: 蓝牙 SPP (Serial Port Profile), ESC/POS 热敏打印指令

**关键文档**:
- `视力中心蓝牙数据汇聚系统-PRD.md`: 产品需求文档 v3.0
- `docs/superpowers/plans/2026-05-23-视力中心蓝牙数据汇聚系统实现计划.md`: 技术实现计划
- `设备接口协议/`: 各设备接口协议文档（PDF/TEXT）

---

## 历史项目经验

⚠️ **重要**: 本项目基于历史项目 PrintServerV5 的问题重构，必须遵循以下原则：

### 之前的问题
1. 代码重复（app.py 和 printing/manager.py）
2. 模块化不完整、职责不清
3. 硬编码魔法数字
4. 平台兼容性问题
5. 打印队列管理不健壮
6. 缺少单元测试

### 强制要求
1. **分层清晰**: API层 → 业务逻辑层 → 设备抽象层 → 硬件抽象层
2. **模块化完整**: 打印机驱动、蓝牙适配器、打印服务、设备管理、数据处理分离
3. **避免硬编码**: ESC/POS命令必须封装成有意义的方法
4. **统一配置管理**: 支持环境变量覆盖
5. **完善的异常体系**: 自定义异常，详细日志
6. **打印队列健壮**: 状态持久化，自动重试
7. **平台适配**: 蓝牙适配器统一接口，Windows/Linux双平台
8. **单元测试**: 核心模块必须有测试

---

## 项目结构

```
F:\CodeWorkSpace\PrintServer-V1\
├── CLAUDE.md                      # 本文档
├── pyproject.toml                 # Python项目配置（待创建）
├── main.py                        # 主入口（待创建）
├── .gitignore                     # Git忽略（待创建）
├── src/                           # 后端源码（待创建）
│   ├── core/                      # 基础设施层
│   │   ├── config.py              # 统一配置管理
│   │   ├── logger.py              # 结构化日志系统
│   │   └── exceptions.py          # 自定义异常体系
│   ├── drivers/                   # 设备驱动层
│   │   ├── escpos_commands.py     # ESC/POS命令封装（无魔法数字）
│   │   └── printer_driver.py      # 打印机驱动
│   ├── adapters/                  # 硬件抽象层
│   │   ├── bluetooth_adapter.py   # 蓝牙适配器抽象接口
│   │   └── windows_bluetooth.py   # Windows蓝牙实现
│   ├── models/                    # 数据模型
│   │   └── data_models.py         # 统一数据模型
│   ├── parsers/                   # 设备数据解析器
│   │   ├── vision_chart_parser.py # 电子视力表解析器（HTTP）
│   │   └── biometer_parser.py     # 眼生物测量仪解析器（蓝牙打印）
│   ├── services/                  # 业务逻辑层
│   │   ├── data_processing_service.py # 数据处理服务
│   │   ├── printing_service.py    # 打印服务
│   │   ├── queue_service.py       # 队列管理服务
│   │   └── device_service.py      # 设备管理服务
│   ├── templates/                 # 打印模板
│   │   └── print_templates.py     # 56mm模板生成器
│   ├── api/                       # API层
│   │   └── routes.py              # FastAPI路由
│   └── mocks/                     # 模拟设备（用于测试）
├── web/                           # 前端源码（待创建）
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       ├── stores/
│       └── views/
├── tests/                         # 单元测试
├── data/                          # SQLite数据存储
├── 设备接口协议/                  # 设备协议文档
└── docs/
    └── superpowers/plans/         # 实现计划文档
```

---

## 核心架构与设计模式

### 分层架构
```
┌─────────────────────────────────┐
│  API层 (FastAPI + Web UI)      │
├─────────────────────────────────┤
│  业务逻辑层 (Services)         │
├─────────────────────────────────┤
│  设备抽象层 (Drivers + Managers)│
├─────────────────────────────────┤
│  硬件抽象层 (Bluetooth Adapter) │
├─────────────────────────────────┤
│  基础设施层 (Config/Log/Exception)│
└─────────────────────────────────┘
```

### 关键设计模式
- **策略模式**: 不同平台蓝牙实现切换
- **工厂模式**: 打印机驱动、设备解析器创建
- **命令模式**: ESC/POS打印指令封装
- **观察者模式**: 数据接收后事件响应

---

## 常用开发命令

### 后端开发
```bash
# 安装依赖
pip install -e .[dev]

# 运行后端服务（推荐端口 8191）
python main.py --port=8191

# 运行测试
pytest tests/
pytest tests/ --cov=src  # 覆盖率测试

# 代码质量检查
flake8 src/
black src/
```

### 前端开发
```bash
# 安装依赖
cd web
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 类型检查
npm run type-check
```

### Windows 服务管理（推荐）

**停止所有服务（快速）：**
```powershell
.\stop-services.ps1
```

**启动方式（推荐 - 稳定）：**
在两个分开的 PowerShell 窗口中运行：
```powershell
# 窗口 1 - 后端
cd F:\CodeWorkSpace\PrintServer-V1
python main.py --port=8191

# 窗口 2 - 前端
cd F:\CodeWorkSpace\PrintServer-V1\web
npm run dev
```

### 访问地址
- **前端界面**: http://localhost:8188
- **API文档**: http://localhost:8191/docs (Swagger)
- **OpenAPI JSON**: http://localhost:8191/openapi.json

### 重要提示
- Windows 上 Uvicorn `--reload` 默认关闭，避免兼容性问题
- 如果需要 reload，使用 `python main.py --port=8191 --reload`
- 端口冲突时运行 `.\stop-services.ps1` 清理

---

## ESC/POS 命令封装规范

⚠️ **禁止直接使用魔法数字**，必须通过方法调用：

```python
# 错误做法 ❌
data = b'\x1b\x40'  # 初始化
data += b'\x1b\x61\x01'  # 居中

# 正确做法 ✅
from src.drivers.escpos_commands import ESCPOSCommands
cmd = ESCPOSCommands()
data = cmd.initialize()
data += cmd.align_center()
```

ESCPOSCommands 必须提供的方法：
- `initialize()` → bytes
- `align_left()`, `align_center()`, `align_right()` → bytes
- `set_bold(on: bool)` → bytes
- `set_font_size(size: int)` → bytes
- `print_qr(data: str)` → List[bytes]
- `line_feed(lines: int = 1)` → bytes
- `cut_paper(full: bool = True)` → bytes

---

## 统一数据模型规范

所有设备数据解析后转换为统一的 CheckRecord 模型：

```python
# src/models/data_models.py 必须包含

class PatientInfo(BaseModel):
    patientName: str
    patientId: str
    phone: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None

class CheckMetadata(BaseModel):
    checkTime: datetime
    deviceType: str  # "vision-chart", "biometer", "tonometer", etc.
    deviceId: Optional[str] = None

class VisionData(BaseModel):
    # 视力表专用数据
    od: Optional[EyeData] = None  # 右眼
    os: Optional[EyeData] = None  # 左眼

class BiometerData(BaseModel):
    # 生物测量仪专用数据
    pass

class CheckRecord(BaseModel):
    id: str
    patientInfo: PatientInfo
    metadata: CheckMetadata
    visionData: Optional[VisionData] = None
    biometerData: Optional[BiometerData] = None
    rawData: Optional[Dict] = None  # 原始数据保留
```

---

## 设备接口规范

### 电子视力表 (HTTP)
- **接收接口**: GET `/api/receive/vision-chart`
- **参数**: visionType, eyes, right, left, resultTime, userName, userId, deviceNumber
- **响应**: `{"code": 0, "message": "success", "data": {"recordId": "xxx"}}`

### 蓝牙打印设备 (SPP)
- 系统模拟蓝牙打印机角色
- 设备发送打印数据流，系统解析提取结构化数据
- 已有的协议文档：生物测量仪、视力筛查仪

### 热敏打印机 (蓝牙)
- **协议**: ESC/POS 标准指令集
- **纸宽**: 56mm
- **二维码**: QR Code, 版本 2-3, 模块大小 6-8dot, 纠错等级 M/Q

---

## 配置管理规范

配置文件使用 JSON 或 YAML，支持环境变量覆盖：

```python
# 配置读取方式
from src.core.config import get_config

config = get_config()
# 配置项:
# config.http.port = 8181
# config.printer.mac_address = "00:11:22:33:44:55"
# config.printer.auto_print = False
# config.bluetooth.auto_reconnect = True
```

环境变量前缀: `VISION_` (例如: `VISION_HTTP_PORT=8181`)

---

## 异常体系规范

```python
# src/core/exceptions.py

class VisionCenterException(Exception):
    """基础异常"""
    pass

class DeviceConnectionError(VisionCenterException):
    """设备连接失败"""
    pass

class DataParseError(VisionCenterException):
    """数据解析失败"""
    pass

class PrintError(VisionCenterException):
    """打印失败"""
    pass
```

---

## 开发检查清单

在提交代码前，请确认：

- [ ] 遵循分层架构，没有跨层调用
- [ ] ESC/POS 命令通过方法调用，无魔法数字
- [ ] 配置统一管理，支持环境变量
- [ ] 自定义异常体系，详细日志
- [ ] 新增代码有对应的单元测试
- [ ] 打印机驱动模块测试覆盖率 ≥80%
- [ ] 数据处理模块测试覆盖率 ≥80%
- [ ] 代码格式化（black/isort/flake8）

---

## 参考文档

详细实现步骤请参考：`docs/superpowers/plans/2026-05-23-视力中心蓝牙数据汇聚系统实现计划.md`

产品需求请参考：`视力中心蓝牙数据汇聚系统-PRD.md`

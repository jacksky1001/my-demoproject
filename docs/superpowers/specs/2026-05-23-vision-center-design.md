# 视力中心蓝牙数据汇聚系统 - 阶段1设计文档

**版本**: 0.1.0
**日期**: 2026-05-23
**阶段**: 1 - 基础设施 + 电子视力表 + 模拟打印机

---

## 1. 概述

基于《视力中心蓝牙数据汇聚系统-PRD.md》v3.0，采用分阶段实现：
- **阶段1**: 基础设施 + 电子视力表 + 模拟打印机
- **阶段2**: 真实蓝牙打印机 + 眼生物测量仪/视力筛查仪
- **阶段3**: 队列管理 + 自动重连 + 数据保留

### 设计原则

1. **分层清晰**: API层 → 业务逻辑层 → 设备抽象层 → 硬件抽象层
2. **模块化完整**: 各模块独立，职责明确
3. **无魔法数字**: ESC/POS命令全部封装为有意义的方法
4. **统一配置管理**: 支持环境变量覆盖
5. **完善异常体系**: 自定义异常，详细日志
6. **先模拟后真实**: 模拟设备优先实现，支持无硬件开发测试

---

## 2. 项目结构

```
F:\CodeWorkSpace\PrintServer-V1\
├── CLAUDE.md
├── pyproject.toml              (待创建)
├── main.py                     (待创建)
├── .gitignore                  (待创建)
├── src/
│   ├── core/                   (基础设施层)
│   │   ├── config.py           配置管理
│   │   ├── logger.py           结构化日志
│   │   └── exceptions.py       自定义异常
│   ├── drivers/                (设备驱动层)
│   │   ├── escpos_commands.py  ESC/POS命令封装
│   │   └── printer_driver.py   打印机驱动(含模拟)
│   ├── models/                 (数据模型)
│   │   └── data_models.py      统一数据模型
│   ├── parsers/                (设备解析器)
│   │   └── vision_chart_parser.py  电子视力表解析
│   ├── services/               (业务逻辑层)
│   │   ├── data_processing_service.py  数据处理
│   │   └── printing_service.py         打印服务
│   ├── templates/              (打印模板)
│   │   └── print_templates.py  56mm模板
│   ├── api/                    (API层)
│   │   └── routes.py           FastAPI路由
│   └── mocks/                  (模拟设备 - P0)
│       └── mock_devices.py     模拟电子视力表
├── web/                        (前端 - Vue3)
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/index.ts
│       ├── stores/index.ts
│       └── views/
├── tests/                      (单元测试)
├── data/                       (数据目录)
├── 设备接口协议/
└── docs/
    └── superpowers/
        ├── plans/
        └── specs/
```

---

## 3. 核心模块设计

### 3.1 src/core/ - 基础设施层

#### 3.1.1 config.py - 配置管理

使用 Pydantic + pydantic-settings 实现统一配置：

```python
class PrinterConfig(BaseModel):
    mac_address: str = ""
    paper_width: int = 56
    auto_print: bool = False
    simulate: bool = True  # 默认模拟模式

class HttpConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8181

class DataConfig(BaseModel):
    db_path: str = "data/vision-center.db"
    retention_days: int = 90

class Config(BaseSettings):
    printer: PrinterConfig = PrinterConfig()
    http: HttpConfig = HttpConfig()
    data: DataConfig = DataConfig()
    log_level: str = "INFO"
    
    model_config = {
        "env_prefix": "VISION_",
        "env_nested_delimiter": "__",
    }
```

环境变量示例：
- `VISION_HTTP_PORT=8181`
- `VISION_PRINTER_AUTO_PRINT=true`

#### 3.1.2 exceptions.py - 异常体系

```python
class VisionCenterException(Exception): pass
class DeviceConnectionError(VisionCenterException): pass
class DataParseError(VisionCenterException): pass
class PrintError(VisionCenterException): pass
class ConfigError(VisionCenterException): pass
```

#### 3.1.3 logger.py - 日志系统

- 避免循环依赖，独立初始化
- 结构化日志格式
- 支持控制台输出

---

### 3.2 src/models/ - 数据模型

使用 Pydantic v2 实现统一数据模型：

```python
class PatientInfo(BaseModel):
    patientName: str
    patientId: str
    phone: Optional[str] = None

class CheckMetadata(BaseModel):
    checkTime: datetime
    deviceType: str  # "vision-chart" / "biometer" / "vision-screening"
    deviceId: Optional[str] = None

class EyeData(BaseModel):
    vision: Optional[str] = None
    logVision: Optional[str] = None

class VisionChartData(BaseModel):
    visionType: Optional[str] = None
    od: Optional[EyeData] = None
    os: Optional[EyeData] = None

class CheckRecord(BaseModel):
    id: str = Field(default_factory=...)
    patientInfo: PatientInfo
    metadata: CheckMetadata
    visionChartData: Optional[VisionChartData] = None
    rawData: Optional[Dict[str, Any]] = None
    printed: bool = False
    printTime: Optional[datetime] = None
```

---

### 3.3 src/drivers/ - 设备驱动层

#### 3.3.1 escpos_commands.py - ESC/POS 命令封装

**禁止魔法数字**，所有命令通过方法调用：

```python
class ESCPOSCommands:
    @staticmethod
    def initialize() -> bytes
    @staticmethod
    def align_left() -> bytes
    @staticmethod
    def align_center() -> bytes
    @staticmethod
    def set_bold(enabled: bool) -> bytes
    @staticmethod
    def set_font_size(width_mult: int, height_mult: int) -> bytes
    @staticmethod
    def text(content: str, encoding: str = 'gbk') -> bytes
    @classmethod
    def print_qr_full(cls, data: str, module_size: int, level: str) -> List[bytes]
    @staticmethod
    def cut_paper(full_cut: bool) -> bytes
```

#### 3.3.2 printer_driver.py - 打印机驱动

```python
class PrinterDriver(ABC):
    @abstractmethod
    def connect() -> bool
    @abstractmethod
    def disconnect() -> None
    @abstractmethod
    def is_connected() -> bool
    @abstractmethod
    def send_data(data: bytes) -> bool
    def print_commands(commands: List[bytes]) -> bool

class SimulatedPrinterDriver(PrinterDriver):
    # 输出到 data/simulated_print.txt

class BluetoothPrinterDriver(PrinterDriver):
    # TBD: 阶段2使用 bleak 实现
```

---

### 3.4 src/mocks/ - 模拟设备 (P0)

```python
def generate_mock_vision_chart_data(patient_name, patient_id) -> CheckRecord
def send_mock_vision_chart_http(server_url, patient_name) -> bool
```

---

### 3.5 src/templates/ - 打印模板

#### PrintTemplate56mm - 56mm 热敏打印机模板

```python
class PrintTemplate56mm:
    def generate_vision_chart_report(self, record: CheckRecord) -> List[bytes]
    def _generate_qr_json(self, record: CheckRecord) -> str
```

QR 码 JSON 格式（PRD 规格）：
```json
{
    "version": "1.0",
    "generateTime": "2026-05-23T...",
    "patientInfo": {
        "name": "...",
        "id": "...",
        "phone": "..."
    },
    "checkData": [
        {
            "deviceType": "vision-chart",
            "checkTime": "...",
            "data": {...}
        }
    ]
}
```

---

### 3.6 src/services/ - 业务逻辑层

#### DataProcessingService
```python
class DataProcessingService:
    @staticmethod
    def parse_vision_chart_http(params: Dict) -> CheckRecord
```

#### PrintingService
```python
class PrintingService:
    def print_record(self, record: CheckRecord, force: bool = None) -> bool
    def test_print(self) -> bool
```

---

### 3.7 src/api/ - API 层 (FastAPI)

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/health | GET | 健康检查 |
| /api/receive/vision-chart | GET | 接收电子视力表数据 |
| /api/records | GET | 获取记录列表 |
| /api/print/{record_id} | POST | 打印指定记录 |
| /api/print/test | POST | 打印测试页 |

---

## 4. 阶段1范围确认

### 已包含
✅ 电子视力表 HTTP 数据接收 (PRD REQ-001a)
✅ 统一数据模型
✅ ESC/POS 命令封装 (PRD REQ-021)
✅ 56mm 打印模板
✅ 模拟打印机 (输出到文件)
✅ 模拟设备 (测试用)
✅ 统一配置管理 (PRD REQ-022)
✅ 日志系统 (PRD OPS-001)
✅ 自定义异常体系 (PRD REQ-023)
✅ FastAPI RESTful API
✅ Vue 3 前端基础框架

### 暂不包含 (后续阶段)
❌ 真实蓝牙打印机连接
❌ 眼生物测量仪/视力筛查仪解析
❌ SQLite 持久化
❌ 打印队列管理 (PRD REQ-024)
❌ 蓝牙自动重连 (PRD REQ-025)

---

## 5. 依赖配置 (pyproject.toml)

```toml
[project]
name = "vision-center-bluetooth-system"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "requests>=2.30.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black",
    "ruff",
]
```

前端依赖见 `web/package.json`。

---

## 6. 快速启动指南

### 后端
```bash
pip install -e .[dev]
python main.py
```

### 前端
```bash
cd web
npm install
npm run dev
```

### 测试
```bash
# 使用模拟设备发送测试数据
python -m src.mocks.mock_devices
```

---

**文档结束**

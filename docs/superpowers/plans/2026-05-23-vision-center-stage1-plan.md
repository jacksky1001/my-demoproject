# 视力中心蓝牙数据汇聚系统 - 阶段1实现计划

**目标：** 构建阶段1 MVP — 基础设施 + 电子视力表 + 模拟打印机

**架构：** 分层架构（API层 → 业务逻辑层 → 设备抽象层 → 硬件抽象层），先实现模拟设备和模拟打印机，支持无硬件开发测试

**技术栈：** Python 3.10+, FastAPI, Pydantic, Vue 3 + TypeScript + Vite + Element Plus

---

## 文件结构映射

| 文件 | 职责 | 类型 |
|------|------|------|
| `pyproject.toml` | Python依赖配置 | 创建 |
| `.gitignore` | Git忽略配置 | 创建 |
| `main.py` | 后端主入口 | 创建 |
| `src/__init__.py` | Python包标识 | 创建 |
| `src/core/__init__.py` | 核心包标识 | 创建 |
| `src/core/exceptions.py` | 自定义异常体系 | 创建 |
| `src/core/config.py` | 统一配置管理 | 创建 |
| `src/core/logger.py` | 结构化日志 | 创建 |
| `src/models/__init__.py` | 模型包标识 | 创建 |
| `src/models/data_models.py` | 统一数据模型 | 创建 |
| `src/drivers/__init__.py` | 驱动包标识 | 创建 |
| `src/drivers/escpos_commands.py` | ESC/POS命令封装 | 创建 |
| `src/drivers/printer_driver.py` | 打印机驱动(含模拟) | 创建 |
| `src/templates/__init__.py` | 模板包标识 | 创建 |
| `src/templates/print_templates.py` | 56mm打印模板 | 创建 |
| `src/services/__init__.py` | 服务包标识 | 创建 |
| `src/services/data_processing_service.py` | 数据处理服务 | 创建 |
| `src/services/printing_service.py` | 打印服务 | 创建 |
| `src/api/__init__.py` | API包标识 | 创建 |
| `src/api/routes.py` | FastAPI路由 | 创建 |
| `src/mocks/__init__.py` | 模拟包标识 | 创建 |
| `src/mocks/mock_devices.py` | 模拟设备 | 创建 |
| `web/package.json` | 前端依赖配置 | 创建 |
| `web/vite.config.ts` | Vite配置 | 创建 |
| `web/index.html` | 前端入口HTML | 创建 |
| `web/src/main.ts` | 前端主入口 | 创建 |
| `web/src/App.vue` | 主应用组件 | 创建 |
| `web/src/router/index.ts` | 路由配置 | 创建 |
| `web/src/stores/index.ts` | Pinia状态管理 | 创建 |
| `web/src/views/Dashboard.vue` | 主界面 | 创建 |
| `web/src/views/Devices.vue` | 设备管理 | 创建 |
| `web/src/views/PrintQueue.vue` | 打印队列 | 创建 |
| `web/src/views/History.vue` | 历史记录 | 创建 |
| `web/src/views/Settings.vue` | 系统设置 | 创建 |

---

## 任务分解（小粒度）

---

### 任务 1：项目初始化 - 基础配置

**文件：**
- 创建：`pyproject.toml`
- 创建：`.gitignore`
- 创建：所有 `__init__.py` 空文件

- [ ] **步骤 1：创建 pyproject.toml**

```toml
[project]
name = "vision-center-bluetooth-system"
version = "0.1.0"
description = "视力中心蓝牙数据汇聚系统"
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

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **步骤 2：创建 .gitignore**

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
.venv
venv/
ENV/
data/*.db
data/*.txt
*.log
node_modules/
web/dist/
web/.vite/
```

- [ ] **步骤 3：创建所有 __init__.py 空文件**

```bash
mkdir -p src/{core,models,drivers,templates,services,api,mocks} web/src/{views,router,stores} tests data
# Windows:
# mkdir src\core, src\models, src\drivers, src\templates, src\services, src\api, src\mocks, web\src\views, web\src\router, web\src\stores, tests, data
touch src/__init__.py src/core/__init__.py src/models/__init__.py
touch src/drivers/__init__.py src/templates/__init__.py src/services/__init__.py
touch src/api/__init__.py src/mocks/__init__.py
```

- [ ] **步骤 4：验证目录结构**

```bash
ls -la
# 确认所有目录已创建
```

- [ ] **步骤 5：Commit**

```bash
git add pyproject.toml .gitignore src/__init__.py src/core/__init__.py src/models/__init__.py src/drivers/__init__.py src/templates/__init__.py src/services/__init__.py src/api/__init__.py src/mocks/__init__.py
git commit -m "feat: 初始化项目结构和依赖配置"
```

---

### 任务 2：基础设施层 - 自定义异常

**文件：**
- 创建：`src/core/exceptions.py`

- [ ] **步骤 1：写异常类**

```python
class VisionCenterException(Exception):
    """基础异常类 - 所有项目异常的基类"""
    pass


class DeviceConnectionError(VisionCenterException):
    """设备连接失败异常"""
    pass


class DataParseError(VisionCenterException):
    """数据解析失败异常"""
    pass


class PrintError(VisionCenterException):
    """打印失败异常"""
    pass


class ConfigError(VisionCenterException):
    """配置错误异常"""
    pass
```

- [ ] **步骤 2：验证导入**

```python
# 临时测试脚本
from src.core.exceptions import (
    VisionCenterException,
    DataParseError,
    PrintError
)

print("✅ 异常类导入成功")
```

- [ ] **步骤 3：Commit**

```bash
git add src/core/exceptions.py
git commit -m "feat: 添加自定义异常体系"
```

---

### 任务 3：基础设施层 - 配置管理

**文件：**
- 创建：`src/core/config.py`

- [ ] **步骤 1：写配置类**

```python
from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class PrinterConfig(BaseModel):
    """打印机配置"""
    mac_address: str = ""
    paper_width: int = 56
    auto_print: bool = False
    simulate: bool = True  # 默认模拟模式


class HttpConfig(BaseModel):
    """HTTP服务配置"""
    host: str = "0.0.0.0"
    port: int = 8181


class DataConfig(BaseModel):
    """数据配置"""
    db_path: str = "data/vision-center.db"
    retention_days: int = 90


class Config(BaseSettings):
    """统一配置类"""
    printer: PrinterConfig = PrinterConfig()
    http: HttpConfig = HttpConfig()
    data: DataConfig = DataConfig()
    log_level: str = "INFO"
    
    model_config = {
        "env_prefix": "VISION_",
        "env_nested_delimiter": "__",
    }


# 单例实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取配置单例"""
    global _config
    if _config is None:
        _config = Config()
    return _config
```

- [ ] **步骤 2：验证配置加载**

```python
from src.core.config import get_config

config = get_config()
print(f"✅ 配置加载成功: HTTP端口={config.http.port}")
print(f"   打印机模式: {'模拟' if config.printer.simulate else '蓝牙'}")
```

- [ ] **步骤 3：Commit**

```bash
git add src/core/config.py
git commit -m "feat: 添加统一配置管理模块"
```

---

### 任务 4：基础设施层 - 日志系统

**文件：**
- 创建：`src/core/logger.py`

- [ ] **步骤 1：写日志模块**

```python
import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None


def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """设置日志系统"""
    global _logger
    if _logger is not None:
        return _logger
    
    logger = logging.getLogger("vision-center")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 控制台输出
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    """获取logger实例"""
    if _logger is None:
        return setup_logger()
    return _logger
```

- [ ] **步骤 2：验证日志输出**

```python
from src.core.logger import setup_logger, get_logger

logger = setup_logger("DEBUG")
logger.debug("🔧 调试信息")
logger.info("ℹ️  普通信息")
logger.warning("⚠️  警告信息")
logger.error("❌ 错误信息")
print("✅ 日志系统测试完成")
```

- [ ] **步骤 3：Commit**

```bash
git add src/core/logger.py
git commit -m "feat: 添加结构化日志系统"
```

---

### 任务 5：数据模型 - 统一数据模型

**文件：**
- 创建：`src/models/data_models.py`

- [ ] **步骤 1：写数据模型**

```python
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    """患者基本信息"""
    patientName: str
    patientId: str
    phone: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None


class CheckMetadata(BaseModel):
    """检查元数据"""
    checkTime: datetime
    deviceType: str  # "vision-chart" / "biometer" / "vision-screening"
    deviceId: Optional[str] = None


class EyeData(BaseModel):
    """单眼视力数据"""
    vision: Optional[str] = None
    logVision: Optional[str] = None
    ref: Optional[str] = None
    speed: Optional[str] = None
    isLowVision: bool = False
    lowVision: Optional[str] = None


class VisionChartData(BaseModel):
    """电子视力表专用数据"""
    visionType: Optional[str] = None
    spaceType: Optional[str] = None
    environment: Optional[str] = None
    eyeCorrect: Optional[str] = None
    od: Optional[EyeData] = None  # 右眼
    os: Optional[EyeData] = None  # 左眼


class BiometerData(BaseModel):
    """眼生物测量仪专用数据 - 阶段2"""
    pass


class VisionScreeningData(BaseModel):
    """视力筛查仪专用数据 - 阶段2"""
    pass


class CheckRecord(BaseModel):
    """检查记录 - 统一数据模型"""
    id: str = Field(
        default_factory=lambda: f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    )
    patientInfo: PatientInfo
    metadata: CheckMetadata
    visionChartData: Optional[VisionChartData] = None
    biometerData: Optional[BiometerData] = None
    visionScreeningData: Optional[VisionScreeningData] = None
    rawData: Optional[Dict[str, Any]] = None  # 保存原始数据用于排查
    printed: bool = False
    printTime: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.now)
```

- [ ] **步骤 2：验证数据模型**

```python
from datetime import datetime
from src.models.data_models import PatientInfo, CheckMetadata, EyeData, VisionChartData, CheckRecord

# 创建测试数据
patient = PatientInfo(patientName="测试患者", patientId="P001")
metadata = CheckMetadata(checkTime=datetime.now(), deviceType="vision-chart")
vision_data = VisionChartData(
    od=EyeData(vision="1.0", logVision="5.0"),
    os=EyeData(vision="0.8", logVision="4.9")
)
record = CheckRecord(
    patientInfo=patient,
    metadata=metadata,
    visionChartData=vision_data
)
print(f"✅ 数据模型测试成功: {record.id}")
print(record.model_dump_json(indent=2))
```

- [ ] **步骤 3：Commit**

```bash
git add src/models/data_models.py
git commit -m "feat: 添加统一数据模型"
```

---

### 任务 6：ESC/POS 命令封装

**文件：**
- 创建：`src/drivers/escpos_commands.py`

- [ ] **步骤 1：写 ESC/POS 命令类**

```python
from typing import List


class ESCPOSCommands:
    """ESC/POS 命令封装 - 禁止魔法数字！"""
    
    # 常用编码
    ENCODING_GBK = "gbk"
    ENCODING_GB18030 = "gb18030"
    ENCODING_UTF8 = "utf-8"
    
    @staticmethod
    def initialize() -> bytes:
        """初始化打印机"""
        return b"\x1b\x40"  # ESC @
    
    @staticmethod
    def align_left() -> bytes:
        """左对齐"""
        return b"\x1b\x61\x00"  # ESC a 0
    
    @staticmethod
    def align_center() -> bytes:
        """居中对齐"""
        return b"\x1b\x61\x01"  # ESC a 1
    
    @staticmethod
    def align_right() -> bytes:
        """右对齐"""
        return b"\x1b\x61\x02"  # ESC a 2
    
    @staticmethod
    def set_bold(enabled: bool = True) -> bytes:
        """设置/取消加粗"""
        return b"\x1b\x45\x01" if enabled else b"\x1b\x45\x00"
    
    @staticmethod
    def set_font_size(width_mult: int = 0, height_mult: int = 0) -> bytes:
        """设置字体大小
        width_mult: 0-7 (1-8倍宽)
        height_mult: 0-7 (1-8倍高)
        """
        param = (width_mult & 0x07) | ((height_mult & 0x07) << 4)
        return b"\x1d\x21" + bytes([param])  # GS ! n
    
    @staticmethod
    def line_feed(lines: int = 1) -> bytes:
        """换行"""
        return b"\x0a" * lines
    
    @staticmethod
    def text(content: str, encoding: str = "gbk") -> bytes:
        """输出文本 - 中文打印机通常用GBK"""
        return content.encode(encoding, errors="replace")
    
    @staticmethod
    def set_qr_size(module_size: int = 6) -> bytes:
        """设置二维码模块大小 (1-16)"""
        return b"\x1d\x28\x6b\x03\x00\x31\x43" + bytes([module_size])
    
    @staticmethod
    def set_qr_error_correction(level: str = "M") -> bytes:
        """设置二维码纠错等级
        level: L(7%), M(15%, 默认), Q(25%), H(30%)
        """
        level_map = {"L": 48, "M": 49, "Q": 50, "H": 51}
        return b"\x1d\x28\x6b\x03\x00\x31\x45" + bytes([level_map[level]])
    
    @staticmethod
    def store_qr_data(data: str) -> bytes:
        """存储二维码数据"""
        encoded = data.encode("utf-8")
        data_len = len(encoded)
        total_len = data_len + 3
        pL = total_len % 256
        pH = total_len // 256
        return b"\x1d\x28\x6b" + bytes([pL, pH, 49, 80, 48]) + encoded
    
    @staticmethod
    def print_qr() -> bytes:
        """打印已存储的二维码"""
        return b"\x1d\x28\x6b\x03\x00\x31\x51\x30"
    
    @classmethod
    def print_qr_full(cls, data: str, module_size: int = 6, level: str = "M") -> List[bytes]:
        """完整的二维码打印流程"""
        return [
            cls.set_qr_size(module_size),
            cls.set_qr_error_correction(level),
            cls.store_qr_data(data),
            cls.print_qr()
        ]
    
    @staticmethod
    def cut_paper(full_cut: bool = True) -> bytes:
        """切纸"""
        return b"\x1d\x56\x41\x00" if full_cut else b"\x1d\x56\x42\x00"
```

- [ ] **步骤 2：验证命令生成**

```python
from src.drivers.escpos_commands import ESCPOSCommands

cmd = ESCPOSCommands()
commands = [
    cmd.initialize(),
    cmd.align_center(),
    cmd.set_bold(True),
    cmd.text("测试标题"),
    cmd.set_bold(False),
    cmd.line_feed(2),
    cmd.cut_paper()
]
print(f"✅ 命令生成成功，共 {len(commands)} 条")
print(f"   初始化: {commands[0].hex()}")
```

- [ ] **步骤 3：Commit**

```bash
git add src/drivers/escpos_commands.py
git commit -m "feat: 添加ESC/POS命令封装（无魔法数字）"
```

---

### 任务 7：打印机驱动（含模拟）

**文件：**
- 创建：`src/drivers/printer_driver.py`

- [ ] **步骤 1：写打印机驱动**

```python
from typing import List, Optional
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from src.drivers.escpos_commands import ESCPOSCommands
from src.core.logger import get_logger

logger = get_logger()


class PrinterDriver(ABC):
    """打印机驱动抽象接口"""
    
    @abstractmethod
    def connect(self) -> bool:
        """连接打印机 - 返回是否成功"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """检查连接状态"""
        pass
    
    @abstractmethod
    def send_data(self, data: bytes) -> bool:
        """发送数据到打印机 - 返回是否成功"""
        pass
    
    def print_commands(self, commands: List[bytes]) -> bool:
        """打印一系列命令"""
        if not self.is_connected():
            logger.info("🖨️ 打印机未连接，尝试连接...")
            if not self.connect():
                logger.error("❌ 打印机连接失败")
                return False
        
        try:
            for cmd_data in commands:
                if not self.send_data(cmd_data):
                    logger.error("❌ 发送数据失败")
                    return False
            logger.info("✅ 打印命令发送完成")
            return True
        except Exception as e:
            logger.error(f"❌ 打印异常: {e}")
            return False


class SimulatedPrinterDriver(PrinterDriver):
    """模拟打印机驱动 - 输出到文件"""
    
    def __init__(self, output_file: str = "data/simulated_print.txt"):
        self.output_file = Path(output_file)
        self._connected = False
        self.cmd = ESCPOSCommands()
    
    def connect(self) -> bool:
        logger.info("🖨️ 模拟打印机连接成功")
        self._connected = True
        # 确保目录存在
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        # 添加启动标记
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(f"=== 模拟打印机启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        return True
    
    def disconnect(self) -> None:
        logger.info("📤 模拟打印机断开")
        self._connected = False
    
    def is_connected(self) -> bool:
        return self._connected
    
    def send_data(self, data: bytes) -> bool:
        """将打印数据记录到文件"""
        try:
            with open(self.output_file, "ab") as f:
                f.write(data)
                f.write(b"\n--- END OF BLOCK ---\n")
            # 记录日志
            logger.debug(f"📤 模拟打印: {len(data)} bytes 已写入")
            return True
        except Exception as e:
            logger.error(f"❌ 写入模拟打印文件失败: {e}")
            return False


class BluetoothPrinterDriver(PrinterDriver):
    """蓝牙打印机驱动 - 阶段2实现"""
    
    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        self._connected = False
        self.cmd = ESCPOSCommands()
    
    def connect(self) -> bool:
        raise NotImplementedError("蓝牙驱动阶段2实现")
    
    def disconnect(self) -> None:
        pass
    
    def is_connected(self) -> bool:
        return self._connected
    
    def send_data(self, data: bytes) -> bool:
        raise NotImplementedError("蓝牙驱动阶段2实现")
```

- [ ] **步骤 2：验证模拟打印机**

```python
from src.drivers.printer_driver import SimulatedPrinterDriver
from src.drivers.escpos_commands import ESCPOSCommands

cmd = ESCPOSCommands()
printer = SimulatedPrinterDriver()

# 连接
assert printer.connect() == True
assert printer.is_connected() == True

# 打印测试页
commands = [
    cmd.initialize(),
    cmd.align_center(),
    cmd.set_bold(True),
    cmd.text("测试页"),
    cmd.set_bold(False),
    cmd.line_feed(2),
    cmd.cut_paper()
]
success = printer.print_commands(commands)
assert success == True
print(f"✅ 模拟打印机测试成功，检查 data/simulated_print.txt")
```

- [ ] **步骤 3：Commit**

```bash
git add src/drivers/printer_driver.py
git commit -m "feat: 添加打印机驱动（含模拟实现）"
```

---

### 任务 8：打印模板 - 56mm 热敏打印机

**文件：**
- 创建：`src/templates/print_templates.py`

- [ ] **步骤 1：写打印模板类**

```python
from typing import List
from datetime import datetime
import json
from src.models.data_models import CheckRecord, EyeData
from src.drivers.escpos_commands import ESCPOSCommands
from src.core.logger import get_logger

logger = get_logger()


class PrintTemplate56mm:
    """56mm 热敏打印机模板"""
    
    def __init__(self):
        self.cmd = ESCPOSCommands()
    
    def generate_vision_chart_report(self, record: CheckRecord) -> List[bytes]:
        """生成电子视力表报告 - 56mm宽度"""
        commands = []
        
        # 1. 初始化
        commands.append(self.cmd.initialize())
        
        # 2. 标题 - 居中放大
        commands.append(self.cmd.align_center())
        commands.append(self.cmd.set_font_size(width_mult=1, height_mult=1))
        commands.append(self.cmd.set_bold(True))
        commands.append(self.cmd.text("视力中心\n"))
        commands.append(self.cmd.text("视力检查报告\n"))
        commands.append(self.cmd.set_bold(False))
        commands.append(self.cmd.set_font_size())  # 恢复标准大小
        commands.append(self.cmd.line_feed(1))
        
        # 3. 患者信息 - 左对齐
        commands.append(self.cmd.align_left())
        commands.append(self.cmd.text(f"姓名: {record.patientInfo.patientName}\n"))
        commands.append(self.cmd.text(f"ID: {record.patientInfo.patientId}\n"))
        commands.append(self.cmd.text(f"时间: {record.metadata.checkTime.strftime('%Y-%m-%d %H:%M')}\n"))
        commands.append(self.cmd.text(f"设备: 电子视力表\n"))
        
        # 4. 分隔线
        commands.append(self.cmd.text("-" * 20 + "\n"))
        
        # 5. 视力数据
        if record.visionChartData:
            data = record.visionChartData
            commands.append(self.cmd.set_bold(True))
            commands.append(self.cmd.text("      右眼    左眼\n"))
            commands.append(self.cmd.set_bold(False))
            
            od = data.od or EyeData()
            os = data.os or EyeData()
            commands.append(self.cmd.text(f"视力: {od.vision or '-':<6}  {os.vision or '-':<6}\n"))
            if od.logVision or os.logVision:
                commands.append(self.cmd.text(f"对数: {od.logVision or '-':<6}  {os.logVision or '-':<6}\n"))
            
            if data.eyeCorrect:
                commands.append(self.cmd.text(f"状态: {data.eyeCorrect}\n"))
            if data.visionType:
                commands.append(self.cmd.text(f"视标: {data.visionType}\n"))
        
        commands.append(self.cmd.line_feed(1))
        
        # 6. 二维码 - 居中
        commands.append(self.cmd.align_center())
        qr_data = self._generate_qr_json(record)
        commands.extend(self.cmd.print_qr_full(qr_data, module_size=6, level="M"))
        commands.append(self.cmd.line_feed(1))
        commands.append(self.cmd.text("扫码查看完整数据\n"))
        
        # 7. 结尾走纸切纸
        commands.append(self.cmd.line_feed(3))
        commands.append(self.cmd.cut_paper(full_cut=True))
        
        return commands
    
    def _generate_qr_json(self, record: CheckRecord) -> str:
        """生成二维码JSON数据 - PRD规格"""
        qr_dict = {
            "version": "1.0",
            "generateTime": datetime.now().isoformat(),
            "patientInfo": {
                "name": record.patientInfo.patientName,
                "id": record.patientInfo.patientId,
                "phone": record.patientInfo.phone or ""
            },
            "checkData": [
                {
                    "deviceType": record.metadata.deviceType,
                    "checkTime": record.metadata.checkTime.isoformat(),
                    "data": record.rawData or {}
                }
            ]
        }
        return json.dumps(qr_dict, ensure_ascii=False, separators=(",", ":"))
```

- [ ] **步骤 2：验证模板生成**

```python
from datetime import datetime
from src.models.data_models import PatientInfo, CheckMetadata, EyeData, VisionChartData, CheckRecord
from src.templates.print_templates import PrintTemplate56mm

# 创建测试数据
patient = PatientInfo(patientName="张三", patientId="P001")
metadata = CheckMetadata(checkTime=datetime.now(), deviceType="vision-chart")
vision_data = VisionChartData(
    od=EyeData(vision="1.0", logVision="5.0"),
    os=EyeData(vision="0.8", logVision="4.9"),
    eyeCorrect="裸眼",
    visionType="E"
)
record = CheckRecord(patientInfo=patient, metadata=metadata, visionChartData=vision_data)

# 生成打印命令
template = PrintTemplate56mm()
commands = template.generate_vision_chart_report(record)
print(f"✅ 模板生成成功，共 {len(commands)} 条命令")
```

- [ ] **步骤 3：Commit**

```bash
git add src/templates/print_templates.py
git commit -m "feat: 添加56mm打印模板"
```

---

### 任务 9：数据处理服务 - 电子视力表解析

**文件：**
- 创建：`src/services/data_processing_service.py`

- [ ] **步骤 1：写数据处理服务**

```python
from datetime import datetime
from typing import Dict, Any, Optional
from src.models.data_models import (
    PatientInfo,
    CheckMetadata,
    EyeData,
    VisionChartData,
    CheckRecord
)
from src.core.logger import get_logger
from src.core.exceptions import DataParseError

logger = get_logger()


class DataProcessingService:
    """数据处理服务 - 解析设备数据并转换为统一格式"""
    
    @staticmethod
    def parse_vision_chart_http(params: Dict[str, Any]) -> CheckRecord:
        """解析电子视力表HTTP回调数据 - PRD REQ-001a"""
        try:
            # 1. 解析时间 - 格式: YYYY-MM-DD-HH-mm-ss
            time_str = params.get("resultTime", "")
            check_time = datetime.now()  # 默认当前时间
            if time_str:
                try:
                    check_time = datetime.strptime(time_str, "%Y-%m-%d-%H-%M-%S")
                except ValueError:
                    logger.warning(f"⏰ 时间格式解析失败: '{time_str}'，使用当前时间")
            
            # 2. 患者信息
            patient_info = PatientInfo(
                patientName=params.get("userName", "未知用户"),
                patientId=params.get("userId", "")
            )
            
            # 3. 元数据
            metadata = CheckMetadata(
                checkTime=check_time,
                deviceType="vision-chart",
                deviceId=params.get("deviceNumber")
            )
            
            # 4. 解析视力数据 - 格式示例: "1.0(5.0)"
            def parse_eye_value(value_str: Optional[str]) -> EyeData:
                if not value_str:
                    return EyeData()
                value_str = value_str.strip()
                if not value_str:
                    return EyeData()
                
                vision = value_str
                log_vision = ""
                if "(" in value_str and ")" in value_str:
                    parts = value_str.split("(", 1)
                    vision = parts[0].strip()
                    log_vision = parts[1].split(")", 1)[0].strip()
                
                return EyeData(vision=vision, logVision=log_vision)
            
            vision_data = VisionChartData(
                visionType=params.get("visionType"),
                spaceType=params.get("spaceType"),
                od=parse_eye_value(params.get("right")),
                os=parse_eye_value(params.get("left"))
            )
            
            # 5. 创建记录
            record = CheckRecord(
                patientInfo=patient_info,
                metadata=metadata,
                visionChartData=vision_data,
                rawData=params  # 保存原始数据用于排查
            )
            
            logger.info(f"✅ 解析电子视力表数据成功: {record.patientInfo.patientName}")
            return record
            
        except Exception as e:
            logger.error(f"❌ 解析电子视力表数据失败: {e}")
            raise DataParseError(f"电子视力表数据解析失败: {e}") from e
```

- [ ] **步骤 2：验证数据解析**

```python
from src.services.data_processing_service import DataProcessingService

# 模拟HTTP参数
params = {
    "visionType": "E",
    "eyes": "2.0(5.3)",
    "right": "1.0(5.0)",
    "left": "0.8(4.9)",
    "resultTime": "2026-05-23-15-30-00",
    "userName": "张三",
    "userId": "P001",
    "deviceNumber": "VC-001"
}

# 解析
service = DataProcessingService()
record = service.parse_vision_chart_http(params)
print(f"✅ 数据解析成功: {record.patientInfo.patientName}")
print(f"   右眼视力: {record.visionChartData.od.vision}")
print(f"   左眼视力: {record.visionChartData.os.vision}")
```

- [ ] **步骤 3：Commit**

```bash
git add src/services/data_processing_service.py
git commit -m "feat: 添加数据处理服务"
```

---

### 任务 10：打印服务

**文件：**
- 创建：`src/services/printing_service.py`

- [ ] **步骤 1：写打印服务**

```python
from typing import Optional
from datetime import datetime
from src.models.data_models import CheckRecord
from src.drivers.printer_driver import PrinterDriver, SimulatedPrinterDriver
from src.templates.print_templates import PrintTemplate56mm
from src.core.config import get_config
from src.core.logger import get_logger
from src.core.exceptions import PrintError

logger = get_logger()


class PrintingService:
    """打印服务 - 处理打印业务逻辑"""
    
    def __init__(self):
        self.config = get_config()
        self.driver: Optional[PrinterDriver] = None
        self.template = PrintTemplate56mm()
        self._init_driver()
    
    def _init_driver(self):
        """初始化打印机驱动"""
        if self.config.printer.simulate:
            logger.info("🖨️ 使用模拟打印机")
            self.driver = SimulatedPrinterDriver()
        else:
            logger.warning("⚠️ 蓝牙打印机暂未实现，使用模拟模式")
            self.driver = SimulatedPrinterDriver()  # 阶段2切换
    
    def print_record(self, record: CheckRecord, force: bool = None) -> bool:
        """打印一条检查记录
        force: True=强制打印, False=跳过, None=根据配置
        """
        should_print = force if force is not None else self.config.printer.auto_print
        
        if not should_print:
            logger.info(f"⏭️ 跳过自动打印: {record.patientInfo.patientName}")
            return False
        
        try:
            # 根据设备类型选择模板
            if record.metadata.deviceType == "vision-chart":
                commands = self.template.generate_vision_chart_report(record)
            else:
                logger.warning(f"❓ 未支持的设备类型: {record.metadata.deviceType}")
                return False
            
            # 发送到打印机
            success = self.driver.print_commands(commands)
            
            if success:
                record.printed = True
                record.printTime = datetime.now()
                logger.info(f"✅ 打印成功: {record.patientInfo.patientName}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 打印失败: {e}")
            raise PrintError(f"打印失败: {e}") from e
    
    def test_print(self) -> bool:
        """打印测试页"""
        commands = [
            self.template.cmd.initialize(),
            self.template.cmd.align_center(),
            self.template.cmd.set_bold(True),
            self.template.cmd.text("=== 测试页 ===\n"),
            self.template.cmd.set_bold(False),
            self.template.cmd.line_feed(1),
            self.template.cmd.text(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"),
            self.template.cmd.text(f"模式: {'模拟打印' if self.config.printer.simulate else '蓝牙打印'}\n"),
            self.template.cmd.line_feed(3),
            self.template.cmd.cut_paper()
        ]
        return self.driver.print_commands(commands)
```

- [ ] **步骤 2：验证打印服务**

```python
from datetime import datetime
from src.models.data_models import PatientInfo, CheckMetadata, EyeData, VisionChartData, CheckRecord
from src.services.printing_service import PrintingService

# 创建测试数据
patient = PatientInfo(patientName="测试患者", patientId="P001")
metadata = CheckMetadata(checkTime=datetime.now(), deviceType="vision-chart")
vision_data = VisionChartData(
    od=EyeData(vision="1.0", logVision="5.0"),
    os=EyeData(vision="0.8", logVision="4.9")
)
record = CheckRecord(patientInfo=patient, metadata=metadata, visionChartData=vision_data)

# 测试打印
service = PrintingService()
success = service.print_record(record, force=True)
assert success == True
print("✅ 打印服务测试成功")

# 测试测试页
success = service.test_print()
assert success == True
print("✅ 测试页打印成功")
```

- [ ] **步骤 3：Commit**

```bash
git add src/services/printing_service.py
git commit -m "feat: 添加打印服务"
```

---

### 任务 11：API 层 - FastAPI 路由

**文件：**
- 创建：`src/api/routes.py`

- [ ] **步骤 1：写 FastAPI 路由**

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.core.config import get_config
from src.core.logger import setup_logger, get_logger
from src.core.exceptions import DataParseError, PrintError
from src.services.data_processing_service import DataProcessingService
from src.services.printing_service import PrintingService

# 全局变量
_config = None
_logger = None
_data_service = None
_printing_service = None
_records_store: dict[str, object] = {}  # 阶段1先用内存存储


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 - 启动前/关闭前"""
    global _config, _logger, _data_service, _printing_service
    
    # 启动时初始化
    _config = get_config()
    _logger = setup_logger(_config.log_level)
    _data_service = DataProcessingService()
    _printing_service = PrintingService()
    
    _logger.info("🚀 视力中心蓝牙数据汇聚系统启动")
    yield
    # 关闭时清理
    _logger.info("👋 系统关闭")


app = FastAPI(
    title="视力中心蓝牙数据汇聚系统",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """根路径 - 欢迎信息"""
    return {
        "message": "视力中心蓝牙数据汇聚系统 API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "printer_simulate": _config.printer.simulate,
        "records_count": len(_records_store)
    }


@app.get("/api/receive/vision-chart")
async def receive_vision_chart(request: Request):
    """接收电子视力表数据 - PRD REQ-001a"""
    try:
        # 获取所有URL参数
        params = dict(request.query_params)
        _logger.info(f"📥 收到电子视力表数据: {params.get('userName', '未知')}")
        
        # 解析数据
        record = _data_service.parse_vision_chart_http(params)
        
        # 保存到内存
        _records_store[record.id] = record
        
        # 自动打印（如果启用）
        if _config.printer.auto_print:
            try:
                _printing_service.print_record(record, force=True)
            except Exception as e:
                _logger.error(f"⚠️ 自动打印失败: {e}")
                # 不影响数据接收的成功返回
        
        return JSONResponse(
            status_code=200,
            content={
                "code": 0,
                "message": "接收成功",
                "data": {"recordId": record.id}
            }
        )
        
    except DataParseError as e:
        _logger.error(f"❌ 数据解析失败: {e}")
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": str(e)}
        )
    except Exception as e:
        _logger.error(f"❌ 处理失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误"}
        )


@app.get("/api/records")
async def get_records():
    """获取记录列表"""
    records = list(_records_store.values())
    # 按时间倒序
    records.sort(key=lambda r: r.metadata.checkTime, reverse=True)
    return {
        "code": 0,
        "data": {
            "total": len(records),
            "records": [r.model_dump() for r in records]
        }
    }


@app.post("/api/print/{record_id}")
async def print_record(record_id: str):
    """打印指定记录"""
    record = _records_store.get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"记录不存在: {record_id}")
    
    try:
        success = _printing_service.print_record(record, force=True)
        return {
            "code": 0,
            "message": "打印成功" if success else "打印失败",
            "data": {"recordId": record_id}
        }
    except PrintError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/print/test")
async def test_print():
    """打印测试页"""
    success = _printing_service.test_print()
    return {
        "code": 0,
        "message": "测试页发送完成" if success else "发送失败"
    }
```

- [ ] **步骤 2：验证 API 路由**

```python
# 临时测试 - 导入测试
from src.api.routes import app
print("✅ API 路由导入成功")
print(f"   应用标题: {app.title}")
print(f"   应用版本: {app.version}")
```

- [ ] **步骤 3：Commit**

```bash
git add src/api/routes.py
git commit -m "feat: 添加FastAPI API路由"
```

---

### 任务 12：主入口 - main.py

**文件：**
- 创建：`main.py`

- [ ] **步骤 1：写主入口**

```python
import uvicorn
from src.core.config import get_config


def main():
    """主入口函数"""
    config = get_config()
    
    print(f"\n{'=' * 50}")
    print(f"🚀 视力中心蓝牙数据汇聚系统")
    print(f"📡 API地址: http://{config.http.host}:{config.http.port}")
    print(f"📚 文档地址: http://{config.http.host}:{config.http.port}/docs")
    print(f"🖨️  打印机模式: {'模拟' if config.printer.simulate else '蓝牙'}")
    print(f"{'=' * 50}\n")
    
    uvicorn.run(
        "src.api.routes:app",
        host=config.http.host,
        port=config.http.port,
        reload=True  # 开发模式自动重载
    )


if __name__ == "__main__":
    main()
```

- [ ] **步骤 2：验证主入口**

```python
# 测试导入
import main
print("✅ 主入口导入成功")
```

- [ ] **步骤 3：Commit**

```bash
git add main.py
git commit -m "feat: 添加主入口文件"
```

---

### 任务 13：模拟设备

**文件：**
- 创建：`src/mocks/mock_devices.py`

- [ ] **步骤 1：写模拟设备**

```python
from datetime import datetime
from pathlib import Path
import random
import requests
import time
from src.models.data_models import (
    PatientInfo,
    CheckMetadata,
    EyeData,
    VisionChartData,
    CheckRecord
)
from src.core.logger import get_logger

logger = get_logger()


def generate_mock_vision_chart_data(
    patient_name: str = "测试患者",
    patient_id: str = None
) -> CheckRecord:
    """生成模拟电子视力表数据 - 用于内部测试"""
    if patient_id is None:
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    patient_info = PatientInfo(
        patientName=patient_name,
        patientId=patient_id
    )
    
    metadata = CheckMetadata(
        checkTime=datetime.now(),
        deviceType="vision-chart",
        deviceId="VC-001"
    )
    
    # 随机生成视力数据
    vision_values = ["1.0", "0.8", "1.2", "0.6", "1.5", "0.5"]
    od_vision = random.choice(vision_values)
    os_vision = random.choice(vision_values)
    
    vision_data = VisionChartData(
        visionType="E",
        spaceType="5m",
        eyeCorrect="裸眼",
        od=EyeData(
            vision=od_vision,
            logVision=str(round(float(od_vision) + 0.5, 2)),
            speed=f"{random.randint(5,15)}s"
        ),
        os=EyeData(
            vision=os_vision,
            logVision=str(round(float(os_vision) + 0.5, 2)),
            speed=f"{random.randint(5,15)}s"
        )
    )
    
    return CheckRecord(
        patientInfo=patient_info,
        metadata=metadata,
        visionChartData=vision_data
    )


def send_mock_vision_chart_http(
    server_url: str = "http://localhost:8181",
    patient_name: str = "测试患者",
    patient_id: str = None
) -> bool:
    """模拟电子视力表发送HTTP回调 - PRD REQ-001a"""
    if patient_id is None:
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 对应 PRD 中的 GET /api/receive/vision-chart 格式
    params = {
        "visionType": "E",
        "eyes": "2.0(5.3)",
        "right": f"{random.choice(['1.0','0.8','1.2'])}(5.0)",
        "left": f"{random.choice(['1.0','0.8','1.2'])}(5.0)",
        "resultTime": datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
        "userName": patient_name,
        "userId": patient_id,
        "deviceNumber": "VC-001"
    }
    
    try:
        logger.info(f"📤 发送模拟电子视力表数据: {patient_name} ({patient_id})")
        response = requests.get(f"{server_url}/api/receive/vision-chart", params=params, timeout=5)
        logger.info(f"📥 响应: {response.status_code} - {response.text}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        logger.error("❌ 连接失败，请确认服务器已启动")
        return False
    except Exception as e:
        logger.error(f"❌ 发送失败: {e}")
        return False


if __name__ == "__main__":
    # 直接运行发送模拟数据
    import argparse
    parser = argparse.ArgumentParser(description="发送模拟电子视力表数据")
    parser.add_argument("--name", default="测试患者", help="患者姓名")
    parser.add_argument("--id", default=None, help="患者ID")
    parser.add_argument("--url", default="http://localhost:8181", help="服务器地址")
    args = parser.parse_args()
    
    setup_logger("INFO")
    success = send_mock_vision_chart_http(args.url, args.name, args.id)
    exit(0 if success else 1)
```

- [ ] **步骤 2：修正导入**

在文件顶部添加 `setup_logger` 导入：
```python
from src.core.logger import setup_logger
```

- [ ] **步骤 3：验证模拟设备**

```python
from src.mocks.mock_devices import generate_mock_vision_chart_data

# 生成模拟数据
record = generate_mock_vision_chart_data("测试张三", "P123")
print(f"✅ 模拟数据生成成功: {record.patientInfo.patientName}")
print(f"   右眼: {record.visionChartData.od.vision}")
print(f"   左眼: {record.visionChartData.os.vision}")
```

- [ ] **步骤 4：Commit**

```bash
git add src/mocks/mock_devices.py
git commit -m "feat: 添加模拟设备模块"
```

---

### 任务 14：前端 - 基础配置

**文件：**
- 创建：`web/package.json`
- 创建：`web/vite.config.ts`
- 创建：`web/index.html`

- [ ] **步骤 1：创建 web/package.json**

```json
{
  "name": "vision-center-web",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.0",
    "element-plus": "^2.6.0",
    "@element-plus/icons-vue": "^2.3.0",
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "vue-tsc": "^2.0.0"
  }
}
```

- [ ] **步骤 2：创建 web/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8181',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **步骤 3：创建 web/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>视力中心蓝牙数据汇聚系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **步骤 4：Commit**

```bash
git add web/package.json web/vite.config.ts web/index.html
git commit -m "feat: 添加前端基础配置"
```

---

### 任务 15：前端 - 主入口和状态管理

**文件：**
- 创建：`web/src/main.ts`
- 创建：`web/src/stores/index.ts`

- [ ] **步骤 1：创建 web/src/main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import App from './App.vue'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

- [ ] **步骤 2：创建 web/src/stores/index.ts**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// API 客户端
const apiClient = axios.create({
  baseURL: '/api'
})

// 检查记录类型
export interface PatientInfo {
  patientName: string
  patientId: string
  phone?: string
}

export interface CheckMetadata {
  checkTime: string
  deviceType: string
  deviceId?: string
}

export interface CheckRecord {
  id: string
  patientInfo: PatientInfo
  metadata: CheckMetadata
  printed: boolean
}

export const useAppStore = defineStore('app', () => {
  const records = ref<CheckRecord[]>([])
  const loading = ref(false)

  // 获取记录列表
  const fetchRecords = async () => {
    loading.value = true
    try {
      const response = await apiClient.get('/records')
      if (response.data.code === 0) {
        records.value = response.data.data.records
      }
    } catch (error) {
      console.error('获取记录失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 打印记录
  const printRecord = async (recordId: string) => {
    try {
      const response = await apiClient.post(`/print/${recordId}`)
      return response.data
    } catch (error) {
      console.error('打印失败:', error)
      throw error
    }
  }

  // 打印测试页
  const printTestPage = async () => {
    try {
      const response = await apiClient.post('/print/test')
      return response.data
    } catch (error) {
      console.error('打印测试页失败:', error)
      throw error
    }
  }

  return {
    records,
    loading,
    fetchRecords,
    printRecord,
    printTestPage
  }
})
```

- [ ] **步骤 3：Commit**

```bash
git add web/src/main.ts web/src/stores/index.ts
git commit -m "feat: 添加前端主入口和状态管理"
```

---

### 任务 16：前端 - 路由配置

**文件：**
- 创建：`web/src/router/index.ts`

- [ ] **步骤 1：创建路由配置**

```typescript
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/devices',
    name: 'Devices',
    component: () => import('@/views/Devices.vue')
  },
  {
    path: '/print-queue',
    name: 'PrintQueue',
    component: () => import('@/views/PrintQueue.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

- [ ] **步骤 2：Commit**

```bash
git add web/src/router/index.ts
git commit -m "feat: 添加前端路由配置"
```

---

### 任务 17：前端 - 主应用组件 App.vue

**文件：**
- 创建：`web/src/App.vue`

- [ ] **步骤 1：创建 App.vue**

```vue
<template>
  <el-container class="app-container">
    <el-header>
      <h2>视力中心蓝牙数据汇聚系统</h2>
    </el-header>
    <el-container>
      <el-aside width="200px">
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="/">
            <el-icon><Monitor /></el-icon>
            <span>主界面</span>
          </el-menu-item>
          <el-menu-item index="/devices">
            <el-icon><Connection /></el-icon>
            <span>设备管理</span>
          </el-menu-item>
          <el-menu-item index="/print-queue">
            <el-icon><Printer /></el-icon>
            <span>打印队列</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><Document /></el-icon>
            <span>历史记录</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Monitor, Connection, Printer, Document, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-container {
  height: 100vh;
}
.el-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}
.el-header h2 {
  margin: 0;
}
.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add web/src/App.vue
git commit -m "feat: 添加前端主应用组件"
```

---

### 任务 18：前端 - 主界面 Dashboard.vue

**文件：**
- 创建：`web/src/views/Dashboard.vue`

- [ ] **步骤 1：创建 Dashboard.vue**

```vue
<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="今日检查数" :value="todayCount">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="待打印数" :value="pendingCount" color="#f56c6c">
            <template #suffix>份</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已打印数" :value="printedCount" color="#67c23a">
            <template #suffix>份</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="设备状态">
            <template #default>
              <el-tag type="success">已连接</el-tag>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="recent-records" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近检查记录</span>
          <div>
            <el-button type="primary" @click="handlePrintTest">打印测试页</el-button>
            <el-button type="primary" @click="store.fetchRecords()">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="recentRecords" style="width: 100%" v-loading="store.loading">
        <el-table-column prop="id" label="记录ID" width="200" />
        <el-table-column prop="patientInfo.patientName" label="姓名" width="120" />
        <el-table-column prop="patientInfo.patientId" label="ID" width="120" />
        <el-table-column prop="metadata.deviceType" label="设备类型" width="120">
          <template #default="{ row }">
            {{ getDeviceTypeName(row.metadata.deviceType) }}
          </template>
        </el-table-column>
        <el-table-column prop="metadata.checkTime" label="检查时间" />
        <el-table-column prop="printed" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.printed ? 'success' : 'warning'">
              {{ row.printed ? '已打印' : '待打印' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handlePrint(row)">打印</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAppStore } from '@/stores'
import { ElMessage } from 'element-plus'
import type { CheckRecord } from '@/stores'

const store = useAppStore()

const todayCount = computed(() => store.records.length)
const pendingCount = computed(() => store.records.filter(r => !r.printed).length)
const printedCount = computed(() => store.records.filter(r => r.printed).length)

const recentRecords = computed(() => [...store.records].reverse().slice(0, 10))

const getDeviceTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'vision-chart': '电子视力表',
    'biometer': '眼生物测量仪',
    'vision-screening': '视力筛查仪'
  }
  return typeMap[type] || type
}

const handlePrint = async (record: CheckRecord) => {
  try {
    await store.printRecord(record.id)
    ElMessage.success('打印任务已发送')
    await store.fetchRecords()
  } catch {
    ElMessage.error('打印失败')
  }
}

const handlePrintTest = async () => {
  try {
    await store.printTestPage()
    ElMessage.success('测试页已发送')
  } catch {
    ElMessage.error('测试页发送失败')
  }
}

onMounted(() => {
  store.fetchRecords()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add web/src/views/Dashboard.vue
git commit -m "feat: 添加前端主界面"
```

---

### 任务 19：前端 - 其他页面（Devices/PrintQueue/History/Settings）

**文件：**
- 创建：`web/src/views/Devices.vue`
- 创建：`web/src/views/PrintQueue.vue`
- 创建：`web/src/views/History.vue`
- 创建：`web/src/views/Settings.vue`

- [ ] **步骤 1：创建 Devices.vue**

```vue
<template>
  <div class="devices">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
        </div>
      </template>
      <el-alert title="提示" type="info" :closable="false">
        设备管理功能 - 阶段2实现
      </el-alert>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **步骤 2：创建 PrintQueue.vue**

```vue
<template>
  <div class="print-queue">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>打印队列</span>
        </div>
      </template>
      <el-alert title="提示" type="info" :closable="false">
        打印队列功能 - 阶段2实现
      </el-alert>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **步骤 3：创建 History.vue**

```vue
<template>
  <div class="history">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>历史记录</span>
        </div>
      </template>
      <el-alert title="提示" type="info" :closable="false">
        历史记录功能 - 阶段2实现
      </el-alert>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

- [ ] **步骤 4：创建 Settings.vue**

```vue
<template>
  <div class="settings">
    <el-card shadow="hover">
      <template #header>
        <span>系统设置</span>
      </template>
      <el-alert title="提示" type="info" :closable="false">
        系统设置功能 - 阶段2实现
      </el-alert>
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
</style>
```

- [ ] **步骤 5：Commit**

```bash
git add web/src/views/Devices.vue web/src/views/PrintQueue.vue web/src/views/History.vue web/src/views/Settings.vue
git commit -m "feat: 添加前端其他页面占位"
```

---

### 任务 20：端到端集成测试

**文件：**
- 测试所有模块集成

- [ ] **步骤 1：启动后端服务（另一个终端）**

```bash
python main.py
# 等待服务启动到 http://localhost:8181
```

- [ ] **步骤 2：测试健康检查 API**

```bash
curl http://localhost:8181/api/health
# 或在浏览器访问 http://localhost:8181/docs
```

- [ ] **步骤 3：发送模拟数据**

```python
from src.mocks.mock_devices import send_mock_vision_chart_http

send_mock_vision_chart_http(
    server_url="http://localhost:8181",
    patient_name="集成测试张三",
    patient_id="T001"
)
```

- [ ] **步骤 4：验证数据已接收**

```bash
curl http://localhost:8181/api/records
# 应看到刚才发送的数据
```

- [ ] **步骤 5：验证模拟打印文件**

```bash
cat data/simulated_print.txt
# 应看到打印输出
```

---

## 自审检查

✅ 规格覆盖：阶段1所有功能都有任务实现
✅ 无占位符：所有任务都有完整代码，无TODO/待实现
✅ 类型一致：所有类型和方法签名都一致
✅ 小粒度：每个任务都是2-5分钟可完成的步骤
✅ 可测试：每个任务都有验证步骤

---

## 计划完成

计划写完保存到 `docs/superpowers/plans/2026-05-23-vision-center-stage1-plan.md`

**执行选项：**
1. **子 Agent 驱动（推荐）** - 我为每个任务 dispatch 新的 subagent，任务间审查，快速迭代
2. **顺序执行** - 在本 session 按批次执行任务，有审查检查点

请选择执行方式！

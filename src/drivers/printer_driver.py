from typing import List, Optional
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from src.drivers.escpos_commands import ESCPOSCommands
from src.core.logger import get_logger
from src.adapters.bluetooth_adapter import BluetoothAdapter
from src.adapters.windows_bluetooth import create_bluetooth_adapter

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
    """蓝牙打印机驱动 - 真实蓝牙实现"""

    def __init__(self, mac_address: str, adapter: Optional[BluetoothAdapter] = None):
        self.mac_address = mac_address
        self.adapter = adapter or create_bluetooth_adapter()
        self.cmd = ESCPOSCommands()
        logger.info(f"🖨️ 蓝牙打印机驱动初始化: {mac_address}")

    def connect(self) -> bool:
        """连接到蓝牙打印机"""
        if not self.adapter.is_available():
            logger.error("❌ 蓝牙适配器不可用")
            return False

        if self.adapter.is_connected():
            return True

        return self.adapter.connect(self.mac_address)

    def disconnect(self) -> None:
        """断开打印机连接"""
        self.adapter.disconnect()

    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.adapter.is_connected()

    def send_data(self, data: bytes) -> bool:
        """发送打印数据"""
        return self.adapter.send_data(data)
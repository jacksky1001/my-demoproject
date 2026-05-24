from typing import List, Optional
from src.adapters.bluetooth_adapter import BluetoothAdapter, BluetoothDevice
from src.core.logger import get_logger

logger = get_logger()


class MockBluetoothAdapter(BluetoothAdapter):
    """模拟蓝牙适配器 - 用于开发测试"""

    def __init__(self):
        self._connected = False
        self._connected_address = None
        self._mock_devices = [
            BluetoothDevice(
                address="00:11:22:33:44:55",
                name="PTP-II (模拟)",
                paired=True,
                connected=False
            ),
            BluetoothDevice(
                address="AA:BB:CC:DD:EE:FF",
                name="Test Printer (模拟)",
                paired=False,
                connected=False
            )
        ]

    def is_available(self) -> bool:
        return True

    def scan_devices(self, duration: int = 8) -> List[BluetoothDevice]:
        logger.info(f"🔍 模拟扫描蓝牙设备 ({duration}秒)...")
        import time
        time.sleep(min(duration, 2))
        logger.info(f"✅ 模拟扫描完成，发现 {len(self._mock_devices)} 个设备")
        return self._mock_devices

    def connect(self, address: str) -> bool:
        logger.info(f"🔗 模拟连接到 {address}...")
        self._connected = True
        self._connected_address = address
        logger.info(f"✅ 模拟连接成功")
        return True

    def disconnect(self) -> None:
        logger.info("📤 模拟断开蓝牙")
        self._connected = False
        self._connected_address = None

    def is_connected(self) -> bool:
        return self._connected

    def send_data(self, data: bytes) -> bool:
        if not self._connected:
            logger.error("❌ 未连接到设备")
            return False
        logger.debug(f"📤 模拟发送: {len(data)} bytes")
        # 同时也写入模拟文件以便调试
        from pathlib import Path
        output_file = Path("data/simulated_print.txt")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "ab") as f:
            f.write(data)
        return True

    def receive_data(self, buffer_size: int = 1024) -> Optional[bytes]:
        return None

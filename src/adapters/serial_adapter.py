import sys
import time
from typing import List, Optional
from src.adapters.bluetooth_adapter import BluetoothAdapter, BluetoothDevice
from src.adapters.com_port_mapper import ComPortMapper
from src.core.logger import get_logger

logger = get_logger()

# 尝试导入 pyserial
try:
    import serial
    import serial.tools.list_ports
    HAVE_PYSERIAL = True
    logger.info("✅ pyserial 已加载")
except ImportError:
    HAVE_PYSERIAL = False
    logger.info("⚠️ pyserial 未安装")


class SerialAdapter(BluetoothAdapter):
    """串口适配器 - 用于连接映射为 COM 口的蓝牙打印机"""

    def __init__(self):
        self._serial: Optional[serial.Serial] = None
        self._connected_port: Optional[str] = None
        self._available = sys.platform == "win32"
        self._com_mapper = ComPortMapper()

    def is_available(self) -> bool:
        return self._available and HAVE_PYSERIAL

    def scan_devices(self, duration: int = 2) -> List[BluetoothDevice]:
        """扫描可用的 COM 口 - 显示真实蓝牙设备名称和MAC地址"""
        devices = []
        try:
            if not HAVE_PYSERIAL:
                logger.warning("pyserial 未安装，无法扫描 COM 口")
                return devices

            logger.info("🔍 扫描可用 COM 口...")

            # 获取COM口映射信息 - com_port_mapper已经处理了所有复杂逻辑
            mappings = self._com_mapper.get_com_port_mappings()

            for mapping in mappings:
                device = BluetoothDevice(
                    address=mapping.port_name,
                    name=mapping.device_name,
                    paired=True,
                    connected=False
                )
                if mapping.is_bluetooth and mapping.mac_address and mapping.mac_address != "Unknown":
                    device.mac_address = mapping.mac_address
                devices.append(device)

                if mapping.is_bluetooth:
                    logger.info(f"发现: {mapping.port_name} - {mapping.device_name} (MAC: {mapping.mac_address})")
                else:
                    logger.info(f"发现: {mapping.port_name} - {mapping.device_name}")

            if not devices:
                logger.info("未发现可用 COM 口")

            logger.info(f"✅ 扫描完成，发现 {len(devices)} 个 COM 口")
            return devices

        except Exception as e:
            logger.error(f"❌ 扫描失败: {e}")
            return []

    def connect(self, address: str) -> bool:
        """连接到 COM 口"""
        try:
            if not HAVE_PYSERIAL:
                logger.error("pyserial 未安装")
                return False

            logger.info(f"🔗 正在连接到 {address}...")
            self.disconnect()

            if not address.upper().startswith("COM"):
                logger.error(f"无效的 COM 口地址: {address}")
                return False

            # 常用打印机波特率
            baud_rates = [9600, 19200, 38400, 57600, 115200]

            for baud in baud_rates:
                try:
                    logger.debug(f"尝试波特率: {baud}")
                    self._serial = serial.Serial(
                        port=address,
                        baudrate=baud,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=2,
                        write_timeout=5
                    )
                    if self._serial.is_open:
                        self._connected_port = address
                        logger.info(f"✅ 连接成功 (波特率: {baud})")
                        return True
                except Exception as e:
                    logger.debug(f"波特率 {baud} 失败: {e}")
                    if self._serial:
                        try:
                            self._serial.close()
                        except Exception:
                            pass
                    self._serial = None

            logger.error("❌ 所有波特率都连接失败")
            return False

        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            self.disconnect()
            return False

    def disconnect(self) -> None:
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        self._connected_port = None
        logger.info("📤 串口已断开")

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def send_data(self, data: bytes) -> bool:
        if not self._serial or not self._serial.is_open:
            logger.error("❌ 未连接到设备")
            return False
        try:
            self._serial.reset_output_buffer()
            total_sent = self._serial.write(data)
            self._serial.flush()
            logger.debug(f"📤 已发送 {total_sent} bytes")
            return True
        except Exception as e:
            logger.error(f"❌ 发送失败: {e}")
            return False

    def receive_data(self, buffer_size: int = 1024) -> Optional[bytes]:
        if not self._serial or not self._serial.is_open:
            return None
        try:
            if self._serial.in_waiting > 0:
                return self._serial.read(min(self._serial.in_waiting, buffer_size))
            return None
        except Exception as e:
            logger.error(f"❌ 接收失败: {e}")
            return None

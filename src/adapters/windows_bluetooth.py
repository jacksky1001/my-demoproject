import sys
import socket
import time
from typing import List, Optional
from src.adapters.bluetooth_adapter import BluetoothAdapter, BluetoothDevice
from src.core.logger import get_logger

logger = get_logger()


class WindowsBluetoothAdapter(BluetoothAdapter):
    """Windows 蓝牙适配器实现 - 使用 RFCOMM Socket"""

    # SPP (Serial Port Profile) UUID
    SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"

    def __init__(self):
        self._socket: Optional[socket.socket] = None
        self._connected_address: Optional[str] = None
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """检查蓝牙是否可用 - 尝试加载 winsock"""
        try:
            # Windows 上检查蓝牙是否开启比较复杂
            # 先简单返回 True，实际连接时会验证
            return sys.platform == "win32"
        except Exception as e:
            logger.warning(f"蓝牙不可用: {e}")
            return False

    def is_available(self) -> bool:
        return self._available

    def scan_devices(self, duration: int = 8) -> List[BluetoothDevice]:
        """扫描蓝牙设备 - Windows 实现"""
        devices = []
        try:
            import subprocess
            import re

            logger.info(f"🔍 开始扫描蓝牙设备 ({duration}秒)...")

            # 方法1: 使用 Windows.Devices.Enumeration via PowerShell (最可靠)
            try:
                ps_cmd = [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    """
                    # 加载 Windows Runtime
                    Add-Type -AssemblyName System.Runtime.WindowsRuntime
                    $asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]

                    # 查找所有蓝牙设备
                    $selector = [Windows.Devices.Enumeration.DeviceInformation]::GetAqsSelector('Bluetooth')
                    $task = [Windows.Devices.Enumeration.DeviceInformation]::FindAllAsync($selector)
                    $task = $asTask.MakeGenericMethod([Windows.Devices.Enumeration.DeviceInformationCollection]).Invoke($null, @($task))
                    $task.Wait()
                    $devices = $task.Result

                    $output = @()
                    foreach ($d in $devices) {
                        if ($d.Name -and $d.Id -match 'Bluetooth#Bluetooth.*(?<mac>[0-9A-Fa-f]{12})') {
                            $mac = $matches['mac'] -replace '(..)(..)(..)(..)(..)(..)', '$1:$2:$3:$4:$5:$6'
                            $output += @{
                                Name = $d.Name
                                Address = $mac.ToUpper()
                                Id = $d.Id
                            }
                        }
                    }
                    $output | ConvertTo-Json
                    """
                ]
                result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=45)
                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        ps_devices = json.loads(result.stdout)
                        if ps_devices:
                            if not isinstance(ps_devices, list):
                                ps_devices = [ps_devices]
                            for dev in ps_devices:
                                name = dev.get("Name", "Unknown")
                                mac = dev.get("Address", "")
                                if mac:
                                    devices.append(BluetoothDevice(
                                        address=mac,
                                        name=name,
                                        paired=True,
                                        connected=False
                                    ))
                            logger.info(f"   WinRT 发现 {len(ps_devices)} 个设备")
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                logger.debug(f"WinRT 扫描失败: {e}")

            # 方法2: 使用更全面的 PowerShell PNP 查询
            if not devices:
                try:
                    ps_cmd = [
                        "powershell",
                        "-Command",
                        """
                        Get-PnpDevice | Where-Object {
                            $_.Class -like '*Bluetooth*' -or
                            $_.FriendlyName -like '*PTP*' -or
                            $_.FriendlyName -like '*Printer*'
                        } | Select-Object FriendlyName, InstanceId, Status | ConvertTo-Json
                        """
                    ]
                    result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0 and result.stdout.strip():
                        import json
                        try:
                            ps_devices = json.loads(result.stdout)
                            if ps_devices:
                                if not isinstance(ps_devices, list):
                                    ps_devices = [ps_devices]
                                for dev in ps_devices:
                                    name = dev.get("FriendlyName", "Unknown")
                                    instance_id = dev.get("InstanceId", "")
                                    mac_match = re.search(r'([0-9A-Fa-f]{12})', instance_id)
                                    if mac_match:
                                        mac_raw = mac_match.group(1)
                                        mac = f"{mac_raw[0:2]}:{mac_raw[2:4]}:{mac_raw[4:6]}:{mac_raw[6:8]}:{mac_raw[8:10]}:{mac_raw[10:12]}".upper()
                                        exists = any(d.address == mac for d in devices)
                                        if not exists:
                                            devices.append(BluetoothDevice(
                                                address=mac,
                                                name=name,
                                                paired=True,
                                                connected=False
                                            ))
                                logger.info(f"   PNP 发现 {len(devices)} 个设备")
                        except json.JSONDecodeError:
                            pass
                except Exception as e:
                    logger.debug(f"PNP 扫描失败: {e}")

            # 方法3: 尝试使用 pybluez
            try:
                import bluetooth
                logger.info("使用 pybluez 扫描...")
                nearby_devices = bluetooth.discover_devices(duration=duration, lookup_names=True, flush_cache=True)
                for addr, name in nearby_devices:
                    addr = addr.upper()
                    exists = any(d.address == addr for d in devices)
                    if not exists:
                        devices.append(BluetoothDevice(
                            address=addr,
                            name=name or "Unknown",
                            paired=False,
                            connected=False
                        ))
                if nearby_devices:
                    logger.info(f"   pybluez 发现 {len(nearby_devices)} 个设备")
            except ImportError:
                logger.info("pybluez 未安装")
            except Exception as e:
                logger.debug(f"pybluez 扫描失败: {e}")

            if not devices:
                logger.info("未自动发现设备，请在 Windows 蓝牙设置中先配对设备，或手动输入 MAC 地址")

            logger.info(f"✅ 扫描完成，共发现 {len(devices)} 个设备")
            return devices

        except Exception as e:
            logger.error(f"❌ 扫描失败: {e}")
            return []

    def connect(self, address: str, port: int = 1) -> bool:
        """连接到蓝牙打印机 - 使用 RFCOMM socket
        address: MAC 地址
        port: RFCOMM 端口（通常是 1）
        """
        try:
            logger.info(f"🔗 正在连接到 {address} (端口 {port})...")

            # 关闭现有连接
            self.disconnect()

            # 创建 RFCOMM socket
            # Windows 上使用 AF_BTH (Bluetooth)
            # 注意：这需要 Python 3.9+ 或 pybluez
            try:
                # 尝试使用 pybluez
                import bluetooth
                self._socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self._socket.connect((address, port))
            except (ImportError, AttributeError):
                # 尝试使用 Windows native socket (AF_BTH)
                # AF_BTH = 32, SOCK_STREAM = 1, BTHPROTO_RFCOMM = 3
                try:
                    import struct
                    self._socket = socket.socket(socket.AF_BTH, socket.SOCK_STREAM, socket.BTHPROTO_RFCOMM)

                    # 转换 MAC 地址为字节序
                    mac_bytes = bytes.fromhex(address.replace(':', ''))
                    # Windows 要求的 BTH_ADDR 格式是小端序
                    mac_bytes = mac_bytes[::-1]

                    # 构建 sockaddr_bth 结构
                    # family (2 bytes) + reserved (2 bytes) + bt_addr (8 bytes) + service_class_id (16 bytes) + port (4 bytes)
                    addr_buffer = bytearray(32)
                    struct.pack_into('<H', addr_buffer, 0, socket.AF_BTH)
                    struct.pack_into('<6s', addr_buffer, 2, mac_bytes)
                    struct.pack_into('<I', addr_buffer, 8, 0)  # service
                    struct.pack_into('<I', addr_buffer, 12, port)  # port

                    self._socket.connect(bytes(addr_buffer))
                except (AttributeError, OSError) as e:
                    logger.error(f"原生 socket 连接失败: {e}")
                    logger.info("💡 提示: 请安装 pybluez 库: pip install pybluez-win10")
                    return False

            self._connected_address = address
            logger.info(f"✅ 已连接到 {address}")
            return True

        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            self.disconnect()
            return False

    def disconnect(self) -> None:
        """断开连接"""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
        self._connected_address = None
        logger.info("📤 蓝牙已断开")

    def is_connected(self) -> bool:
        return self._socket is not None

    def send_data(self, data: bytes) -> bool:
        """发送数据到打印机"""
        if not self._socket:
            logger.error("❌ 未连接到设备")
            return False

        try:
            total_sent = 0
            while total_sent < len(data):
                sent = self._socket.send(data[total_sent:])
                if sent == 0:
                    logger.error("❌ 连接已关闭")
                    return False
                total_sent += sent
            logger.debug(f"📤 已发送 {total_sent} bytes")
            return True
        except Exception as e:
            logger.error(f"❌ 发送失败: {e}")
            return False

    def receive_data(self, buffer_size: int = 1024) -> Optional[bytes]:
        """接收数据（可选）"""
        if not self._socket:
            return None

        try:
            self._socket.settimeout(1.0)
            return self._socket.recv(buffer_size)
        except socket.timeout:
            return None
        except Exception as e:
            logger.error(f"❌ 接收失败: {e}")
            return None


# 便捷函数
def create_bluetooth_adapter() -> BluetoothAdapter:
    """创建适合当前平台的蓝牙适配器"""
    if sys.platform == "win32":
        return WindowsBluetoothAdapter()
    else:
        logger.warning(f"平台 {sys.platform} 暂不支持完整蓝牙功能，使用模拟模式")
        # 返回模拟适配器
        from src.adapters.mock_bluetooth import MockBluetoothAdapter
        return MockBluetoothAdapter()

"""
COM口与蓝牙设备映射器 - 通过Windows注册表和WMI获取蓝牙设备的真实名称和MAC地址
参考printServerV5的实现思路
"""
import sys
import re
import subprocess
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from src.core.logger import get_logger

logger = get_logger()


@dataclass
class ComPortMapping:
    """COM口映射信息"""
    port_name: str          # COM口号，如 "COM3"
    device_name: str        # 设备真实名称，如 "PTP-II Printer"
    mac_address: str        # MAC地址，如 "60:6e:41:xx:xx:xx"
    is_bluetooth: bool      # 是否是蓝牙设备
    hwid: Optional[str] = None  # 硬件ID


class ComPortMapper:
    """COM口映射器 - 关联COM口与蓝牙设备信息"""

    def __init__(self):
        self._is_windows = sys.platform == "win32"
        # 已知的设备模式 - 来自printServerV5
        self._printer_prefixes = {
            '60:6E:41': 'PTP-II Printer',  # PTP-II设备MAC前缀
        }

    def get_com_port_mappings(self) -> List[ComPortMapping]:
        """获取所有COM口的映射信息"""
        mappings: List[ComPortMapping] = []

        if not self._is_windows:
            logger.warning("非Windows平台，无法获取蓝牙COM口映射")
            return mappings

        try:
            # 首先尝试用pyserial获取基本信息
            # 因为pyserial能给我们很好的描述和hwid
            mappings.extend(self._query_via_pyserial())

            # 补充PowerShell信息
            if mappings:
                self._enhance_with_powershell(mappings)

            return mappings

        except Exception as e:
            logger.error(f"获取COM口映射失败: {e}")
            return mappings

    def _query_via_pyserial(self) -> List[ComPortMapping]:
        """使用pyserial查询端口信息 - 这能给我们hwid"""
        mappings: List[ComPortMapping] = []

        try:
            import serial
            import serial.tools.list_ports

            ports = serial.tools.list_ports.comports()

            for port in ports:
                port_name = port.device.upper()
                description = port.description or port_name
                hwid = port.hwid or ""

                # 判断是否是蓝牙设备
                is_bluetooth = self._is_bluetooth_device(description, hwid)

                # 提取MAC地址
                mac = self._extract_mac_from_hwid(hwid)
                if not mac and is_bluetooth:
                    mac = "Unknown"

                # 获取友好设备名称
                friendly_name = self._get_friendly_name(description, mac)

                mapping = ComPortMapping(
                    port_name=port_name,
                    device_name=friendly_name,
                    mac_address=mac,
                    is_bluetooth=is_bluetooth,
                    hwid=hwid
                )
                mappings.append(mapping)

                if is_bluetooth:
                    logger.info(f"发现蓝牙COM口: {port_name} - {friendly_name} (MAC: {mac})")

        except ImportError:
            logger.warning("pyserial未安装，无法使用此方法")
        except Exception as e:
            logger.debug(f"pyserial查询失败: {e}")

        return mappings

    def _enhance_with_powershell(self, mappings: List[ComPortMapping]):
        """用PowerShell补充更多信息"""
        try:
            cmd = [
                "powershell", "-Command",
                """
                Get-PnpDevice -Class Ports |
                Where-Object { $_.Status -eq 'OK' } |
                ForEach-Object {
                    $port = ''
                    if ($_.FriendlyName -match '(COM\\d+)') { $port = $matches[1] }
                    elseif ($_.Name -match '(COM\\d+)') { $port = $matches[1] }

                    if (-not $port) { return }

                    [PSCustomObject]@{
                        Port = $port
                        Name = $_.FriendlyName
                        InstanceId = $_.InstanceId
                    }
                } | ConvertTo-Json -AsArray
                """
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                import json
                try:
                    ps_devices = {d.get("Port", "").upper(): d for d in json.loads(result.stdout)}

                    # 补充信息
                    for mapping in mappings:
                        if mapping.port_name in ps_devices:
                            ps_dev = ps_devices[mapping.port_name]
                            # 如果pyserial的描述不够好，尝试用PowerShell的
                            if "Device" in mapping.device_name or len(mapping.device_name) < 10:
                                ps_name = ps_dev.get("Name", "")
                                if ps_name and "COM" in ps_name:
                                    mapping.device_name = self._get_friendly_name(ps_name, mapping.mac_address)

                            # 尝试从InstanceId提取MAC
                            if (not mapping.mac_address or mapping.mac_address == "Unknown") and mapping.is_bluetooth:
                                instance_id = ps_dev.get("InstanceId", "")
                                mac_from_instance = self._extract_mac_from_instance_id(instance_id)
                                if mac_from_instance:
                                    mapping.mac_address = mac_from_instance
                                    # 更新友好名称
                                    mapping.device_name = self._get_friendly_name(mapping.device_name, mac_from_instance)

                except json.JSONDecodeError:
                    pass

        except Exception as e:
            logger.debug(f"PowerShell增强失败: {e}")

    def _is_bluetooth_device(self, description: str, hwid: str) -> bool:
        """判断是否为蓝牙设备"""
        desc_lower = description.lower()
        hwid_upper = hwid.upper()

        # 检查关键词
        bluetooth_keywords = [
            "bluetooth", "btlink", "bth", "bthmodem", "spp",
            "serial over bluetooth", "标准串口"
        ]

        for kw in bluetooth_keywords:
            if kw in desc_lower:
                return True

        # 检查HWID
        if "BTHENUM" in hwid_upper or "BLUETOOTH" in hwid_upper:
            return True

        return False

    def _extract_mac_from_hwid(self, hwid: str) -> str:
        """从硬件ID中提取MAC地址"""
        if not hwid:
            return ""

        # 模式匹配 - 查找12位十六进制
        patterns = [
            r'[_\-&]([0-9A-Fa-f]{12})[_\-&]',  # 被分隔符包围的
            r'[_\-&]([0-9A-Fa-f]{12})$',       # 在结尾的
            r'_([0-9A-Fa-f]{12})_',            # 下划线包围的
            r'&([0-9A-Fa-f]{12})&',            # &符号包围的
            r'([0-9A-Fa-f]{12})',              # 任何12位十六进制
        ]

        for pattern in patterns:
            match = re.search(pattern, hwid)
            if match:
                mac_hex = match.group(1)
                if self._is_likely_mac(mac_hex):
                    return ":".join([mac_hex[i:i+2] for i in range(0, 12, 2)])

        return ""

    def _extract_mac_from_instance_id(self, instance_id: str) -> str:
        """从实例ID中提取MAC地址"""
        return self._extract_mac_from_hwid(instance_id)  # 复用同一逻辑

    def _is_likely_mac(self, mac_hex: str) -> bool:
        """判断是否可能是MAC地址"""
        if len(mac_hex) != 12:
            return False

        # 排除明显不是的
        if all(c == '0' for c in mac_hex) or all(c.upper() == 'F' for c in mac_hex):
            return False

        return True

    def _get_friendly_name(self, original_name: str, mac: str) -> str:
        """获取友好的设备名称"""
        # 检查MAC前缀
        if mac and mac != "Unknown":
            mac_prefix = mac[:8].upper()  # 取前3字节
            if mac_prefix in self._printer_prefixes:
                return self._printer_prefixes[mac_prefix]

        # 检查名称中的模式
        original_lower = original_name.lower()

        if "ptp" in original_lower:
            return "PTP-II Printer"
        if "printer" in original_lower or "thermal" in original_lower:
            return "Thermal Printer"
        if "vision" in original_lower or "eye" in original_lower:
            return "Vision Device"

        # 如果描述包含"Standard Serial over Bluetooth"，简化显示
        if "standard serial over bluetooth" in original_lower or "标准串口" in original_lower:
            if mac and mac != "Unknown":
                mac_prefix = mac[:8].upper()
                if mac_prefix == "60:6E:41":
                    return "PTP-II Printer"
                return f"Bluetooth Device ({mac[-8:]})"
            return "Bluetooth Serial Device"

        return original_name

    def _query_via_registry(self) -> List[ComPortMapping]:
        """通过注册表查询（备选方法）"""
        mappings: List[ComPortMapping] = []

        try:
            import winreg

            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"HARDWARE\\DEVICEMAP\\SERIALCOMM")

            try:
                index = 0
                while True:
                    try:
                        device_name, port_name, _ = winreg.EnumValue(key, index)

                        is_bluetooth = "Bluetooth" in device_name or "BTHENUM" in device_name.upper()

                        mappings.append(ComPortMapping(
                            port_name=port_name,
                            device_name=device_name,
                            mac_address="Unknown" if is_bluetooth else "",
                            is_bluetooth=is_bluetooth
                        ))

                        index += 1
                    except OSError:
                        break
            finally:
                winreg.CloseKey(key)

        except Exception as e:
            logger.debug(f"注册表查询失败: {e}")

        return mappings

    def get_mapping_for_port(self, port_name: str) -> Optional[ComPortMapping]:
        """获取指定COM口的映射信息"""
        mappings = self.get_com_port_mappings()
        for m in mappings:
            if m.port_name.upper() == port_name.upper():
                return m
        return None

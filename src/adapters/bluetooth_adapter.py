from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BluetoothDevice:
    """蓝牙设备信息"""
    address: str  # MAC 地址 或 COM 口号
    name: str  # 设备名称
    device_class: Optional[int] = None
    paired: bool = False
    connected: bool = False
    mac_address: Optional[str] = None  # 真实蓝牙MAC地址（串口模式下使用）


class BluetoothAdapter(ABC):
    """蓝牙适配器抽象接口"""

    @abstractmethod
    def is_available(self) -> bool:
        """检查蓝牙适配器是否可用"""
        pass

    @abstractmethod
    def scan_devices(self, duration: int = 8) -> List[BluetoothDevice]:
        """扫描附近的蓝牙设备
        duration: 扫描时长（秒）
        """
        pass

    @abstractmethod
    def connect(self, address: str) -> bool:
        """连接到指定 MAC 地址的设备"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开当前连接"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """检查连接状态"""
        pass

    @abstractmethod
    def send_data(self, data: bytes) -> bool:
        """发送数据到已连接设备"""
        pass

    @abstractmethod
    def receive_data(self, buffer_size: int = 1024) -> Optional[bytes]:
        """从已连接设备接收数据"""
        pass

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
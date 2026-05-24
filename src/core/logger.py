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

    # 控制台输出 - 使用UTF-8编码处理emoji
    handler = logging.StreamHandler(sys.stdout)
    handler.setStream(sys.stdout)
    # Python 3.7+ reconfigures the stream encoding
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
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
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
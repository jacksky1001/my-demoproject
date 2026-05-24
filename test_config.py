from src.core.config import get_config

config = get_config()
print(f"[OK] 配置加载成功: HTTP端口={config.http.port}")
print(f"     打印机模式: {'模拟' if config.printer.simulate else '蓝牙'}")
print(f"     数据保留天数: {config.data.retention_days}天")
print(f"     日志级别: {config.log_level}")
print(f"     数据库路径: {config.data.db_path}")
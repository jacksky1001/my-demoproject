import sys
import os
import socket
import time
import uvicorn
from src.core.config import get_config


def is_port_in_use(host: str, port: int) -> bool:
    """检查端口是否被占用"""
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((host, port))
        return result == 0
    except Exception:
        return False
    finally:
        if s:
            s.close()


def main():
    """主入口函数"""
    config = get_config()

    # 命令行参数优先覆盖端口
    port = config.http.port
    host = config.http.host
    reload_mode = True

    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
        elif arg.startswith("--host="):
            host = arg.split("=", 1)[1]
        elif arg == "--no-reload":
            reload_mode = False

    # 检查端口占用
    if is_port_in_use(host, port):
        print(f"\n⚠️  警告: 端口 {port} 已被占用！")
        print("   请先运行: .\\stop-services.ps1\n")
        response = input("   是否尝试强制启动? (y/N): ")
        if response.lower() != "y":
            print("   已取消启动")
            sys.exit(1)
        print()

    print(f"\n{'=' * 50}")
    print(f"[SYSTEM] 视力中心蓝牙数据汇聚系统")
    print(f"[API] API地址: http://{host}:{port}")
    print(f"[DOCS] 文档地址: http://{host}:{port}/docs")
    print(f"[PRINTER] 打印机模式: {'模拟' if config.printer.simulate else '蓝牙'}")
    print(f"[RELOAD] 自动重载: {'开启' if reload_mode else '关闭'}")
    print(f"{'=' * 50}\n")

    uvicorn.run(
        "src.api.routes:app",
        host=host,
        port=port,
        reload=reload_mode,
        workers=1 if reload_mode else None
    )


if __name__ == "__main__":
    main()
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from urllib.parse import parse_qs
import json
from src.core.config import get_config
from src.core.logger import setup_logger, get_logger
from src.core.exceptions import DataParseError, PrintError
from src.services.data_processing_service import DataProcessingService
from src.services.printing_service import PrintingService
from src.services.record_storage_service import RecordStorageService
from src.adapters.bluetooth_adapter import BluetoothDevice
from src.adapters.windows_bluetooth import WindowsBluetoothAdapter
from src.adapters.serial_adapter import SerialAdapter

# 全局变量
_config = None
_logger = None
_data_service = None
_printing_service = None
_record_storage = None
_bluetooth_adapter = None
_connected_device: dict[str, object] | None = None
_records_store: dict[str, object] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 - 启动前/关闭前"""
    global _config, _logger, _data_service, _printing_service, _record_storage, _bluetooth_adapter, _records_store

    # 启动时初始化
    _config = get_config()
    _logger = setup_logger(_config.log_level)
    _data_service = DataProcessingService()
    _printing_service = PrintingService()
    _record_storage = RecordStorageService(_config.data.db_path, _config.data.retention_days)
    _records_store = _record_storage.load_records()
    _logger.info(f"历史记录已加载: count={len(_records_store)}, db={_config.data.db_path}, retention_days={_config.data.retention_days}")

    # 初始化适配器（先尝试串口，更稳定）
    _bluetooth_adapter = None
    try:
        serial_adapter = SerialAdapter()
        if serial_adapter.is_available():
            _bluetooth_adapter = serial_adapter
            _logger.info("使用串口适配器（推荐）")
    except Exception as e:
        _logger.debug(f"串口适配器初始化失败: {e}")

    if not _bluetooth_adapter:
        _bluetooth_adapter = WindowsBluetoothAdapter()
        _logger.info("使用蓝牙适配器")

    _logger.info("🚀 视力中心蓝牙数据汇聚系统启动")
    yield
    # 关闭时清理
    if _bluetooth_adapter:
        _bluetooth_adapter.disconnect()
    _logger.info("👋 系统关闭")


app = FastAPI(
    title="视力中心蓝牙数据汇聚系统",
    version="0.1.0",
    lifespan=lifespan
)


VISION_CHART_KEYS = {"visionType", "eyes", "right", "left", "f", "resultTime", "userName", "userId", "userld", "deviceNumber"}
VISION_CHART_JSON_KEYS = {"Name", "phone", "birthday", "gender", "SpaceType", "EyeVersion", "Environment", "EyeCorrect", "TestMode", "OpenMirror", "DeviceName", "DateTime", "Result"}


@app.get("/")
async def root(request: Request):
    """根路径 - 欢迎信息或电子视力表回调兼容入口"""
    if VISION_CHART_KEYS.intersection(request.query_params.keys()):
        return await _handle_vision_chart_params(dict(request.query_params))

    return {
        "message": "视力中心蓝牙数据汇聚系统 API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.post("/")
async def root_post(request: Request):
    """兼容设备以POST方式推送电子视力表数据"""
    params = await _extract_request_data(request)
    if _is_vision_chart_json(params):
        matched_keys = sorted(VISION_CHART_JSON_KEYS.intersection(params.keys()))
        _logger.info(f"电子视力表POST根路径匹配JSON字段: {matched_keys}")
        return await _handle_vision_chart_json(params)

    matched_keys = sorted(VISION_CHART_KEYS.intersection(params.keys()))
    if matched_keys:
        _logger.info(f"电子视力表POST根路径匹配URL字段: {matched_keys}")
        return await _handle_vision_chart_params(params)

    _logger.warning(
        "POST / 未识别为电子视力表数据: "
        f"client={_client_host(request)}, content_type={request.headers.get('content-type', '')}, "
        f"parsed_keys={sorted(params.keys())}"
    )
    return JSONResponse(
        status_code=200,
        content={
            "code": 0,
            "message": "ignored",
            "detail": "POST payload received but no vision chart fields were found"
        }
    )


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "printer_simulate": _config.printer.simulate,
        "records_count": len(_records_store)
    }


def _store_record(record):
    _records_store[record.id] = record
    if _record_storage:
        _record_storage.save_record(record)


def _auto_print_record(record):
    if not _config.printer.auto_print:
        _logger.info(f"自动打印未启用，记录进入待打印队列: record_id={record.id}")
        return

    try:
        success = _printing_service.print_record(record, force=True)
        if success:
            _store_record(record)
        _logger.info(f"自动打印执行完成: record_id={record.id}, success={success}, printed={record.printed}")
    except Exception as e:
        _logger.error(f"⚠️ 自动打印失败: record_id={record.id}, error={e}")


@app.get("/api/receive/vision-chart")
async def receive_vision_chart(request: Request):
    """接收电子视力表数据 - PRD REQ-001a"""
    return await _handle_vision_chart_params(dict(request.query_params))


@app.post("/api/receive/vision-chart")
async def receive_vision_chart_post(request: Request):
    """兼容POST方式接收电子视力表数据"""
    params = await _extract_request_data(request)
    if _is_vision_chart_json(params):
        return await _handle_vision_chart_json(params)
    return await _handle_vision_chart_params(params)


def _client_host(request: Request) -> str:
    return request.client.host if request.client else "unknown"


async def _extract_request_data(request: Request) -> dict:
    params = dict(request.query_params)
    content_type = request.headers.get("content-type", "")
    raw_body = await request.body()
    body_preview = raw_body[:500].decode("utf-8", errors="replace") if raw_body else ""

    _logger.info(
        "解析回调请求: "
        f"method={request.method}, path={request.url.path}, client={_client_host(request)}, "
        f"content_type={content_type or '<empty>'}, query_keys={sorted(params.keys())}, "
        f"body_bytes={len(raw_body)}, body_preview={body_preview!r}"
    )

    if raw_body:
        if "application/json" in content_type:
            _merge_json_body(params, raw_body)
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            form = await request.form()
            params.update(dict(form))
        else:
            _merge_raw_body(params, raw_body)

    _logger.info(f"回调请求解析完成: parsed_keys={sorted(params.keys())}")
    return params


def _merge_json_body(params: dict, raw_body: bytes):
    try:
        body = json.loads(raw_body.decode("utf-8-sig", errors="replace"))
        if isinstance(body, dict):
            params.update(body)
    except Exception as e:
        _logger.warning(f"JSON请求体解析失败，尝试按原始文本解析: {e}")
        _merge_raw_body(params, raw_body)


def _merge_raw_body(params: dict, raw_body: bytes):
    text = raw_body.decode("utf-8-sig", errors="replace").strip()
    if not text:
        return

    if text.startswith("{") and text.endswith("}"):
        try:
            body = json.loads(text)
            if isinstance(body, dict):
                params.update(body)
                return
        except Exception as e:
            _logger.warning(f"原始JSON文本解析失败: {e}")

    parsed = parse_qs(text, keep_blank_values=True)
    if parsed:
        params.update({key: values[-1] if values else "" for key, values in parsed.items()})
        return

    for part in text.replace("\r", "\n").split("\n"):
        if "=" in part:
            key, value = part.split("=", 1)
            params[key.strip()] = value.strip()


def _is_vision_chart_json(params: dict) -> bool:
    result = params.get("Result")
    return isinstance(result, dict) and ("OD" in result or "OS" in result)


async def _save_vision_chart_record(record):
    _store_record(record)
    _logger.info(
        "电子视力表记录已保存: "
        f"record_id={record.id}, patient={record.patientInfo.patientName}, "
        f"device_id={record.metadata.deviceId or ''}, total_records={len(_records_store)}"
    )
    _auto_print_record(record)
    return JSONResponse(
        status_code=200,
        content={
            "code": 0,
            "message": "success",
            "data": {"recordId": record.id}
        }
    )


async def _handle_vision_chart_params(params: dict):
    try:
        _logger.info(
            "📥 收到电子视力表URL参数数据: "
            f"name={params.get('userName', '未知')}, "
            f"userId={params.get('userId') or params.get('userld') or ''}, "
            f"device={params.get('deviceNumber') or ''}, "
            f"right={params.get('right') or ''}, left={params.get('left') or params.get('f') or ''}, "
            f"eyes={params.get('eyes') or ''}, auto_print={_config.printer.auto_print}"
        )

        record = _data_service.parse_vision_chart_http(params)
        return await _save_vision_chart_record(record)

    except DataParseError as e:
        _logger.error(f"Data parse failed: {e}")
        return JSONResponse(status_code=400, content={"code": 400, "message": str(e)})
    except Exception as e:
        _logger.error(f"Process failed: {e}")
        return JSONResponse(status_code=500, content={"code": 500, "message": "Server error"})


async def _handle_vision_chart_json(params: dict):
    try:
        result = params.get("Result") or {}
        od = result.get("OD") or {}
        os = result.get("OS") or {}
        _logger.info(
            "📥 收到电子视力表JSON结果数据: "
            f"name={params.get('Name') or ''}, "
            f"device={params.get('DeviceName') or ''}, time={params.get('DateTime') or ''}, "
            f"space={params.get('SpaceType') or ''}, chart={params.get('EyeVersion') or ''}, "
            f"environment={params.get('Environment') or ''}, correction={params.get('EyeCorrect') or ''}, "
            f"od={od.get('vision') or ''}({od.get('logVision') or ''}), od_speed={od.get('speed') or ''}, "
            f"os={os.get('vision') or ''}({os.get('logVision') or ''}), os_speed={os.get('speed') or ''}, "
            f"auto_print={_config.printer.auto_print}"
        )

        record = _data_service.parse_vision_chart_json_object(params)
        return await _save_vision_chart_record(record)

    except DataParseError as e:
        _logger.error(f"Vision chart JSON parse failed: {e}")
        return JSONResponse(status_code=400, content={"code": 400, "message": str(e)})
    except Exception as e:
        _logger.error(f"Vision chart JSON process failed: {e}")
        return JSONResponse(status_code=500, content={"code": 500, "message": "Server error"})


@app.post("/api/pull/vision-chart")
async def pull_vision_chart(request: Request):
    """主动从电子视力表设备拉取数据"""
    try:
        body = await request.json()
        records = _data_service.fetch_vision_chart_pull(
            ip=body.get("ip", ""),
            port=int(body.get("port", 8181)),
            mode=body.get("mode", "latest"),
            start=body.get("start"),
            end=body.get("end")
        )

        record_ids = []
        for record in records:
            _store_record(record)
            record_ids.append(record.id)
            _auto_print_record(record)

        return {
            "code": 0,
            "message": "success",
            "data": {"count": len(record_ids), "recordIds": record_ids}
        }
    except DataParseError as e:
        _logger.error(f"Vision chart pull failed: {e}")
        return JSONResponse(status_code=400, content={"code": 400, "message": str(e)})
    except Exception as e:
        _logger.error(f"Vision chart pull process failed: {e}")
        return JSONResponse(status_code=500, content={"code": 500, "message": "Server error"})


@app.get("/api/settings/printer")
async def get_printer_settings():
    """获取当前打印配置"""
    return {
        "code": 0,
        "data": {
            "autoPrint": _config.printer.auto_print,
            "simulatePrint": _config.printer.simulate,
            "paperWidth": _config.printer.paper_width,
            "printerMac": _config.printer.mac_address
        }
    }


@app.post("/api/settings/printer")
async def update_printer_settings(request: Request):
    """更新运行时打印配置"""
    body = await request.json()
    if "autoPrint" in body:
        _config.printer.auto_print = bool(body["autoPrint"])
    if "simulatePrint" in body:
        _config.printer.simulate = bool(body["simulatePrint"])
    if "paperWidth" in body:
        _config.printer.paper_width = int(body["paperWidth"])
    if "printerMac" in body:
        _config.printer.mac_address = body["printerMac"] or ""

    return {
        "code": 0,
        "message": "success",
        "data": {
            "autoPrint": _config.printer.auto_print,
            "simulatePrint": _config.printer.simulate,
            "paperWidth": _config.printer.paper_width,
            "printerMac": _config.printer.mac_address
        }
    }


@app.post("/api/receive/biometer")
async def receive_biometer(request: Request):
    """接收眼生物测量仪数据"""
    try:
        body = await request.json()
        _logger.info(f"Received biometer data: {body.get('patientName', 'unknown')}")
        record = _data_service.parse_biometer_dict(body)
        _store_record(record)
        if _config.printer.auto_print:
            try:
                if _printing_service.print_record(record, force=True):
                    _store_record(record)
            except Exception as e:
                _logger.error(f"Auto print failed: {e}")
        return JSONResponse(status_code=200, content={
            "code": 0, "message": "receive success", "data": {"recordId": record.id}
        })
    except DataParseError as e:
        return JSONResponse(status_code=400, content={"code": 400, "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})


@app.post("/api/receive/vision-screening")
async def receive_vision_screening(request: Request):
    """接收视力筛查仪数据"""
    try:
        body = await request.json()
        _logger.info(f"Received vision screening data: {body.get('patientName', 'unknown')}")
        record = _data_service.parse_vision_screening_dict(body)
        _store_record(record)
        if _config.printer.auto_print:
            try:
                if _printing_service.print_record(record, force=True):
                    _store_record(record)
            except Exception as e:
                _logger.error(f"Auto print failed: {e}")
        return JSONResponse(status_code=200, content={
            "code": 0, "message": "receive success", "data": {"recordId": record.id}
        })
    except DataParseError as e:
        return JSONResponse(status_code=400, content={"code": 400, "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})


@app.get("/api/records")
async def get_records():
    """获取记录列表"""
    records = list(_records_store.values())
    # 按时间倒序
    records.sort(key=lambda r: r.metadata.checkTime, reverse=True)
    return {
        "code": 0,
        "data": {
            "total": len(records),
            "records": [r.model_dump() for r in records]
        }
    }


@app.post("/api/print/{record_id}")
async def print_record(record_id: str):
    """打印指定记录"""
    record = _records_store.get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"记录不存在: {record_id}")

    try:
        success = _printing_service.print_record(record, force=True)
        if success:
            _store_record(record)
        return {
            "code": 0,
            "message": "打印成功" if success else "打印失败",
            "data": {"recordId": record_id}
        }
    except PrintError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/print/test")
async def test_print():
    """打印测试页"""
    success = _printing_service.test_print()
    return {
        "code": 0,
        "message": "测试页发送完成" if success else "发送失败"
    }


@app.get("/api/print/preview/{record_id}")
async def preview_print(record_id: str):
    """获取热敏打印预览文本"""
    record = _records_store.get(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"记录不存在: {record_id}")

    try:
        template = _printing_service.template
        commands = template.generate_vision_chart_report(record)
        # 提取可打印文本并模拟热敏打印效果
        preview_lines = _build_thermal_preview(record, commands)
        return {
            "code": 0,
            "data": {
                "record": record.model_dump(),
                "preview": preview_lines
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/print/latest-output")
async def latest_print_output():
    """获取最近一次模拟打印的原始输出"""
    import os
    output_file = "data/simulated_print.txt"
    try:
        if os.path.exists(output_file):
            with open(output_file, "rb") as f:
                raw = f.read()
            # 尝试解码，跳过 ESC/POS 控制码
            text_parts = []
            i = 0
            data = raw
            while i < len(data):
                b = data[i]
                if b == 0x1B:  # ESC
                    text_parts.append(f"[ESC+{chr(data[i+1]) if i+1 < len(data) else '?'}]")
                    i += 2
                elif b == 0x1D:  # GS
                    text_parts.append(f"[GS+{chr(data[i+1]) if i+1 < len(data) else '?'}]")
                    i += 2
                elif b == 0x0A:  # LF
                    text_parts.append("\n")
                    i += 1
                elif 0x20 <= b < 0x7F or b >= 0x80:
                    # Try to decode as GBK text segment
                    seg = bytearray()
                    while i < len(data) and (0x20 <= data[i] < 0x7F or data[i] >= 0x80):
                        if data[i] == 0x1B or data[i] == 0x1D or data[i] == 0x0A:
                            break
                        seg.append(data[i])
                        i += 1
                    try:
                        text_parts.append(bytes(seg).decode("gbk", errors="replace"))
                    except:
                        text_parts.append(repr(bytes(seg)))
                else:
                    text_parts.append(f"[{b:02X}]")
                    i += 1
            return {"code": 0, "data": {"output": "".join(text_parts)}}
        else:
            return {"code": 0, "data": {"output": ""}}
    except Exception as e:
        return {"code": 500, "message": str(e)}


def _build_thermal_preview(record, commands: list) -> list:
    """构建热敏打印预览"""
    lines = []
    for cmd in commands:
        try:
            text = cmd.decode("gbk", errors="replace").strip()
            if text:
                lines.append(text)
        except:
            pass
    return lines


# ============ 蓝牙设备管理 API ============

@app.get("/api/bluetooth/scan")
async def scan_bluetooth_devices(duration: int = 8):
    """扫描附近的蓝牙设备"""
    if not _bluetooth_adapter or not _bluetooth_adapter.is_available():
        raise HTTPException(status_code=501, detail="蓝牙适配器不可用")

    try:
        devices = _bluetooth_adapter.scan_devices(duration=duration)

        _logger.info(f"扫描到 {len(devices)} 个设备")
        for d in devices:
            _logger.info(f"  - 地址: {d.address}, 名称: {d.name}, 配对: {d.paired}")

        connected_address = _connected_device.get("address") if _connected_device else None
        return {
            "code": 0,
            "data": {
                "devices": [
                    {
                        "address": d.address,
                        "name": d.name,
                        "paired": d.paired,
                        "connected": d.address == connected_address and _bluetooth_adapter.is_connected(),
                        "mac_address": d.mac_address if d.mac_address else None
                    }
                    for d in devices
                ]
            }
        }
    except Exception as e:
        _logger.error(f"扫描失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bluetooth/status")
async def get_bluetooth_status():
    """获取蓝牙状态"""
    if not _bluetooth_adapter:
        return {"code": 0, "data": {"available": False, "connected": False}}

    connected = _bluetooth_adapter.is_connected()
    return {
        "code": 0,
        "data": {
            "available": _bluetooth_adapter.is_available(),
            "connected": connected,
            "device": _connected_device if connected else None
        }
    }


@app.post("/api/bluetooth/connect")
async def connect_bluetooth_device(request: Request):
    """连接到蓝牙设备"""
    global _connected_device
    if not _bluetooth_adapter or not _bluetooth_adapter.is_available():
        raise HTTPException(status_code=501, detail="蓝牙适配器不可用")

    body = await request.json()
    address = body.get("address")
    device_name = body.get("name") or address
    mac_address = body.get("mac_address")
    if not address:
        raise HTTPException(status_code=400, detail="需要提供 MAC 地址")

    try:
        success = _bluetooth_adapter.connect(address)
        if success:
            # 检查是否是模拟适配器
            adapter_class = _bluetooth_adapter.__class__.__name__
            if adapter_class != "MockBluetoothAdapter" and _printing_service:
                # 真实适配器才切换打印驱动
                from src.drivers.printer_driver import BluetoothPrinterDriver
                _printing_service.set_printer_driver(BluetoothPrinterDriver(address, _bluetooth_adapter))
            _connected_device = {
                "address": address,
                "name": device_name,
                "mac_address": mac_address,
                "paired": True,
                "connected": True
            }
            return {"code": 0, "message": "连接成功", "data": _connected_device}
        else:
            raise HTTPException(status_code=500, detail="连接失败")
    except Exception as e:
        _logger.error(f"连接失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bluetooth/disconnect")
async def disconnect_bluetooth_device():
    """断开蓝牙连接"""
    global _connected_device
    if _bluetooth_adapter:
        _bluetooth_adapter.disconnect()
        # 恢复模拟模式
        if _printing_service:
            from src.drivers.printer_driver import SimulatedPrinterDriver
            _printing_service.set_printer_driver(SimulatedPrinterDriver())
    _connected_device = None
    return {"code": 0, "message": "已断开"}


@app.post("/api/bluetooth/mode")
async def set_bluetooth_mode(request: Request):
    """切换适配器模式 (serial/bluetooth)"""
    global _bluetooth_adapter, _connected_device

    body = await request.json()
    mode = body.get("mode", "serial")

    # 断开现有连接
    if _bluetooth_adapter:
        _bluetooth_adapter.disconnect()
    _connected_device = None

    if mode == "serial":
        try:
            _bluetooth_adapter = SerialAdapter()
            if _bluetooth_adapter.is_available():
                _logger.info("已切换到串口适配器模式")
                return {"code": 0, "message": "已切换到串口模式", "data": {"mode": "serial"}}
        except Exception as e:
            _logger.error(f"串口模式初始化失败: {e}")

        # 回退
        _bluetooth_adapter = WindowsBluetoothAdapter()
        return {"code": 0, "message": "串口不可用，已回退到蓝牙模式", "data": {"mode": "bluetooth"}}

    else:
        _bluetooth_adapter = WindowsBluetoothAdapter()
        _logger.info("已切换到蓝牙适配器模式")
        return {"code": 0, "message": "已切换到蓝牙模式", "data": {"mode": "bluetooth"}}


@app.get("/api/bluetooth/mode")
async def get_bluetooth_mode():
    """获取当前适配器模式"""
    if not _bluetooth_adapter:
        return {"code": 0, "data": {"mode": "unknown"}}

    class_name = _bluetooth_adapter.__class__.__name__
    if "Serial" in class_name:
        return {"code": 0, "data": {"mode": "serial"}}
    elif "Windows" in class_name:
        return {"code": 0, "data": {"mode": "bluetooth"}}
    else:
        return {"code": 0, "data": {"mode": class_name}}
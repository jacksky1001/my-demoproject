"""
阶段1集成测试 - 验证所有模块能正确导入和基本功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("视力中心蓝牙数据汇聚系统 - 阶段1集成测试")
print("=" * 60)

all_passed = True


def test_pass(name: str):
    print(f"✅ {name} - 通过")


def test_fail(name: str, error: Exception):
    global all_passed
    all_passed = False
    print(f"❌ {name} - 失败: {error}")


# 1. 测试基础设施层
print("\n[1/6] 测试基础设施层...")
try:
    from src.core.config import get_config
    from src.core.logger import setup_logger
    from src.core.exceptions import (
        VisionCenterException,
        DataParseError,
        PrintError
    )
    config = get_config()
    logger = setup_logger("INFO")
    test_pass("基础设施层导入")
    print(f"   - HTTP端口: {config.http.port}")
    print(f"   - 打印机模式: {'模拟' if config.printer.simulate else '蓝牙'}")
except Exception as e:
    test_fail("基础设施层导入", e)


# 2. 测试数据模型
print("\n[2/6] 测试数据模型...")
try:
    from datetime import datetime
    from src.models.data_models import (
        PatientInfo, CheckMetadata, EyeData, VisionChartData, CheckRecord
    )
    # 创建测试记录
    patient = PatientInfo(patientName="测试患者", patientId="P001")
    metadata = CheckMetadata(checkTime=datetime.now(), deviceType="vision-chart")
    vision_data = VisionChartData(od=EyeData(vision="1.0"), os=EyeData(vision="0.8"))
    record = CheckRecord(
        patientInfo=patient,
        metadata=metadata,
        visionChartData=vision_data
    )
    test_pass("数据模型创建和序列化")
    print(f"   - 记录ID: {record.id}")
    print(f"   - 患者: {record.patientInfo.patientName}")
except Exception as e:
    test_fail("数据模型", e)


# 3. 测试驱动和命令
print("\n[3/6] 测试ESC/POS命令和打印机驱动...")
try:
    from src.drivers.escpos_commands import ESCPOSCommands
    from src.drivers.printer_driver import SimulatedPrinterDriver
    cmd = ESCPOSCommands()
    printer = SimulatedPrinterDriver()
    assert printer.connect() == True
    test_pass("驱动初始化和连接")
    print(f"   - 驱动已连接: {printer.is_connected()}")
except Exception as e:
    test_fail("驱动和命令", e)


# 4. 测试打印模板
print("\n[4/6] 测试打印模板...")
try:
    from datetime import datetime
    from src.models.data_models import (
        PatientInfo, CheckMetadata, EyeData, VisionChartData, CheckRecord
    )
    from src.templates.print_templates import PrintTemplate56mm
    patient = PatientInfo(patientName="测试患者", patientId="P001")
    metadata = CheckMetadata(checkTime=datetime.now(), deviceType="vision-chart")
    vision_data = VisionChartData(od=EyeData(vision="1.0"), os=EyeData(vision="0.8"))
    record = CheckRecord(patientInfo=patient, metadata=metadata, visionChartData=vision_data)
    template = PrintTemplate56mm()
    commands = template.generate_vision_chart_report(record)
    test_pass("打印模板生成")
    print(f"   - 生成命令数: {len(commands)}")
except Exception as e:
    test_fail("打印模板", e)


# 5. 测试数据处理服务
print("\n[5/6] 测试数据处理服务...")
try:
    from src.services.data_processing_service import DataProcessingService
    service = DataProcessingService()
    params = {
        "visionType": "E",
        "eyes": "2.0(5.3)",
        "right": "1.0(5.0)",
        "f": "0.8(4.9)",
        "resultTime": "2026-05-23-15-30-00",
        "userName": "测试患者",
        "userId": "P001",
        "deviceNumber": "VC-001"
    }
    record = service.parse_vision_chart_http(params)
    assert record.visionChartData.eyes.vision == "2.0"
    assert record.visionChartData.eyes.logVision == "5.3"
    assert record.visionChartData.os.vision == "0.8"

    pulled = service.parse_vision_chart_json_object({
        "Name": "测试患者",
        "phone": "13800000000",
        "birthday": "2010-01-01",
        "gender": "男",
        "SpaceType": "5m",
        "EyeVersion": "E",
        "Environment": "标高",
        "EyeCorrect": "裸眼",
        "TestMode": "正常测试",
        "OpenMirror": False,
        "DeviceName": "VC-001",
        "DateTime": "2025-08-15 16:43:34",
        "Result": {
            "OD": {
                "vision": "0.3",
                "logVision": "4.5",
                "subVision": "",
                "ref": "316.2",
                "isLowVision": False,
                "lowVision": "",
                "speed": "9s"
            },
            "OS": {
                "vision": "",
                "logVision": "",
                "subVision": "",
                "ref": "",
                "isLowVision": True,
                "lowVision": "<0.1(4.0)",
                "speed": "7s"
            }
        }
    })
    assert pulled.patientInfo.patientName == "测试患者"
    assert pulled.metadata.deviceId == "VC-001"
    assert pulled.visionChartData.deviceName == "VC-001"
    assert pulled.visionChartData.testMode == "正常测试"
    assert pulled.visionChartData.openMirror is False
    assert pulled.visionChartData.od.ref == "316.2"
    assert pulled.visionChartData.os.isLowVision is True
    assert pulled.visionChartData.os.lowVision == "<0.1(4.0)"
    assert pulled.visionChartData.os.speed == "7s"

    test_pass("数据解析")
    print(f"   - 解析双眼视力: {record.visionChartData.eyes.vision}")
    print(f"   - 解析右眼视力: {record.visionChartData.od.vision}")
    print(f"   - 解析左眼视力: {record.visionChartData.os.vision}")
except Exception as e:
    test_fail("数据处理服务", e)


# 6. 测试记录持久化存储
print("\n[6/8] 测试记录持久化存储...")
try:
    from tempfile import TemporaryDirectory
    from datetime import datetime
    from src.models.data_models import PatientInfo, CheckMetadata, EyeData, VisionChartData, CheckRecord
    from src.services.record_storage_service import RecordStorageService

    with TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "records.db")
        storage = RecordStorageService(db_path, retention_days=90)
        record = CheckRecord(
            patientInfo=PatientInfo(patientName="持久化患者", patientId="PERSIST-001"),
            metadata=CheckMetadata(checkTime=datetime.now(), deviceType="vision-chart", deviceId="VC-PERSIST"),
            visionChartData=VisionChartData(od=EyeData(vision="2.0", logVision="5.3"))
        )
        storage.save_record(record)
        loaded = RecordStorageService(db_path, retention_days=90).load_records()
        assert record.id in loaded
        assert loaded[record.id].patientInfo.patientName == "持久化患者"
        assert loaded[record.id].visionChartData.od.vision == "2.0"
    test_pass("记录持久化存储")
except Exception as e:
    test_fail("记录持久化存储", e)


# 7. 测试真实电子视力表JSON回调
print("\n[7/8] 测试真实电子视力表JSON回调...")
try:
    from fastapi.testclient import TestClient
    from src.api.routes import app

    payload = {
        "Name": "",
        "phone": "",
        "birthday": "",
        "gender": "",
        "SpaceType": "5m",
        "EyeVersion": "E",
        "Environment": "标高",
        "EyeCorrect": "裸眼",
        "TestMode": "正常测试",
        "OpenMirror": False,
        "DeviceName": "wesdf3454",
        "DateTime": "2026-05-24 13:32:58",
        "Result": {
            "OD": {
                "vision": "2.0",
                "logVision": "5.3",
                "subVision": "",
                "ref": "50.1",
                "isLowVision": False,
                "lowVision": "",
                "speed": "10s"
            },
            "OS": {
                "vision": "1.5",
                "logVision": "5.2",
                "subVision": "",
                "ref": "63.1",
                "isLowVision": False,
                "lowVision": "",
                "speed": "12s"
            }
        }
    }
    with TestClient(app) as client:
        response = client.post("/", json=payload)
        data = response.json()
        assert response.status_code == 200
        assert data["code"] == 0
        assert data["message"] == "success"
        record_id = data["data"]["recordId"]
        records_response = client.get("/api/records")
        records = records_response.json()["data"]["records"]
        saved = next(r for r in records if r["id"] == record_id)
        assert saved["patientInfo"]["patientName"] == "未知用户"
        assert saved["metadata"]["deviceId"] == "wesdf3454"
        assert saved["visionChartData"]["od"]["vision"] == "2.0"
        assert saved["visionChartData"]["od"]["ref"] == "50.1"
        assert saved["visionChartData"]["od"]["speed"] == "10s"
        assert saved["visionChartData"]["os"]["vision"] == "1.5"
    test_pass("真实电子视力表JSON回调")
except Exception as e:
    test_fail("真实电子视力表JSON回调", e)


# 7. 测试打印服务
print("\n[8/8] 测试打印服务...")
try:
    from datetime import datetime
    from src.models.data_models import (
        PatientInfo, CheckMetadata, EyeData, VisionChartData, CheckRecord
    )
    from src.services.printing_service import PrintingService
    patient = PatientInfo(patientName="测试患者", patientId="P001")
    metadata = CheckMetadata(checkTime=datetime.now(), deviceType="vision-chart")
    vision_data = VisionChartData(od=EyeData(vision="1.0"), os=EyeData(vision="0.8"))
    record = CheckRecord(patientInfo=patient, metadata=metadata, visionChartData=vision_data)
    service = PrintingService()
    success = service.print_record(record, force=True)
    test_pass("打印服务")
    print(f"   - 打印结果: {'成功' if success else '失败'}")
except Exception as e:
    test_fail("打印服务", e)


# 测试总结
print("\n" + "=" * 60)
if all_passed:
    print("🎉 阶段1集成测试 - 全部通过！")
    print("\n下一步：")
    print("1. 安装后端依赖: pip install -e .[dev]")
    print("2. 启动后端服务: python main.py")
    print("3. 在另一个终端测试: python -m src.mocks.mock_devices --name 张三")
    print("4. 访问 API 文档: http://localhost:8181/docs")
else:
    print("❌ 部分测试失败，请检查错误信息")
print("=" * 60)
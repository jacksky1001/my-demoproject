from datetime import datetime
from pathlib import Path
import random
import requests
import time
from src.models.data_models import (
    PatientInfo, CheckMetadata, EyeData, VisionChartData,
    BiometerData, BiometerEyeData,
    VisionScreeningData, VisionScreeningEyeData,
    CheckRecord
)
from src.core.logger import setup_logger, get_logger

logger = get_logger()


def generate_mock_vision_chart_data(
    patient_name: str = "测试患者",
    patient_id: str = None
) -> CheckRecord:
    """生成模拟电子视力表数据 - 用于内部测试"""
    if patient_id is None:
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"

    patient_info = PatientInfo(
        patientName=patient_name,
        patientId=patient_id
    )

    metadata = CheckMetadata(
        checkTime=datetime.now(),
        deviceType="vision-chart",
        deviceId="VC-001"
    )

    # 随机生成视力数据
    vision_values = ["1.0", "0.8", "1.2", "0.6", "1.5", "0.5"]
    od_vision = random.choice(vision_values)
    os_vision = random.choice(vision_values)

    vision_data = VisionChartData(
        visionType="E",
        spaceType="5m",
        eyeCorrect="裸眼",
        od=EyeData(
            vision=od_vision,
            logVision=str(round(float(od_vision) + 0.5, 2)),
            speed=f"{random.randint(5,15)}s"
        ),
        os=EyeData(
            vision=os_vision,
            logVision=str(round(float(os_vision) + 0.5, 2)),
            speed=f"{random.randint(5,15)}s"
        )
    )

    return CheckRecord(
        patientInfo=patient_info,
        metadata=metadata,
        visionChartData=vision_data
    )


def send_mock_vision_chart_http(
    server_url: str = "http://localhost:8181",
    patient_name: str = "测试患者",
    patient_id: str = None
) -> bool:
    """模拟电子视力表发送HTTP回调 - PRD REQ-001a"""
    if patient_id is None:
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 对应 PRD 中的 GET /api/receive/vision-chart 格式
    params = {
        "visionType": "E",
        "eyes": "2.0(5.3)",
        "right": f"{random.choice(['1.0','0.8','1.2'])}(5.0)",
        "left": f"{random.choice(['1.0','0.8','1.2'])}(5.0)",
        "resultTime": datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
        "userName": patient_name,
        "userId": patient_id,
        "deviceNumber": "VC-001"
    }

    try:
        logger.info(f"📤 发送模拟电子视力表数据: {patient_name} ({patient_id})")
        response = requests.get(f"{server_url}/api/receive/vision-chart", params=params, timeout=5)
        logger.info(f"📥 响应: {response.status_code} - {response.text}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        logger.error("❌ 连接失败，请确认服务器已启动")
        return False
    except Exception as e:
        logger.error(f"Send failed: {e}")
        return False


def generate_mock_biometer_data(patient_name: str = "测试患者", patient_id: str = None) -> CheckRecord:
    """生成模拟眼生物测量仪数据"""
    if patient_id is None:
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"

    patient_info = PatientInfo(patientName=patient_name, patientId=patient_id)
    metadata = CheckMetadata(
        checkTime=datetime.now(),
        deviceType="biometer",
        deviceId="BM-001"
    )

    def rand_eye_data():
        al = str(round(random.uniform(22.0, 26.0), 2))
        k1 = str(round(random.uniform(42.0, 45.0), 2))
        k2 = str(round(random.uniform(43.0, 46.0), 2))
        return BiometerEyeData(
            al=al,
            k1=k1,
            k2=k2,
            km=str(round((float(k1) + float(k2)) / 2, 2)),
            astig=str(round(abs(float(k2) - float(k1)), 2)),
            acd=str(round(random.uniform(2.5, 3.8), 2)),
            lt=str(round(random.uniform(3.5, 4.5), 2)),
            wtW=str(round(random.uniform(10.5, 12.5), 2)),
            snr=str(round(random.uniform(80, 200), 1))
        )

    biometer_data = BiometerData(
        od=rand_eye_data(),
        os=rand_eye_data(),
        calculationMode="SRK/T"
    )

    return CheckRecord(
        patientInfo=patient_info,
        metadata=metadata,
        biometerData=biometer_data
    )


def generate_mock_vision_screening_data(patient_name: str = "测试患者", patient_id: str = None) -> CheckRecord:
    """生成模拟视力筛查仪数据"""
    if patient_id is None:
        patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"

    patient_info = PatientInfo(patientName=patient_name, patientId=patient_id)
    metadata = CheckMetadata(
        checkTime=datetime.now(),
        deviceType="vision-screening",
        deviceId="VS-001"
    )

    sph_values = ["-0.50", "-1.00", "-2.00", "-2.50", "-3.00", "-1.50", "0.00", "+0.50"]
    cyl_values = ["-0.50", "-0.75", "-1.00", "-1.25", "-1.50", "-0.25"]
    axis_values = ["180", "175", "170", "165", "5", "10", "90", "85"]

    od = VisionScreeningEyeData(
        sph=random.choice(sph_values),
        cyl=random.choice(cyl_values),
        axis=random.choice(axis_values),
        va=f"{random.choice(['1.0', '0.8', '0.9', '1.2'])}",
        pupil=f"{round(random.uniform(3.0, 5.0), 1)}"
    )
    os = VisionScreeningEyeData(
        sph=random.choice(sph_values),
        cyl=random.choice(cyl_values),
        axis=random.choice(axis_values),
        va=f"{random.choice(['1.0', '0.8', '0.9', '1.2'])}",
        pupil=f"{round(random.uniform(3.0, 5.0), 1)}"
    )

    screening_data = VisionScreeningData(
        od=od, os=os,
        pd=str(round(random.uniform(58, 65), 1)),
        examMode="Auto"
    )

    return CheckRecord(
        patientInfo=patient_info,
        metadata=metadata,
        visionScreeningData=screening_data
    )


if __name__ == "__main__":
    # 直接运行发送模拟数据
    import argparse
    parser = argparse.ArgumentParser(description="发送模拟电子视力表数据")
    parser.add_argument("--name", default="测试患者", help="患者姓名")
    parser.add_argument("--id", default=None, help="患者ID")
    parser.add_argument("--url", default="http://localhost:8181", help="服务器地址")
    args = parser.parse_args()

    setup_logger("INFO")
    success = send_mock_vision_chart_http(args.url, args.name, args.id)
    exit(0 if success else 1)
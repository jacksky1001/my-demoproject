from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    """患者基本信息"""
    patientName: str
    patientId: str
    phone: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None


class CheckMetadata(BaseModel):
    """检查元数据"""
    checkTime: datetime
    deviceType: str  # "vision-chart" / "biometer" / "vision-screening"
    deviceId: Optional[str] = None


class EyeData(BaseModel):
    """单眼视力数据"""
    vision: Optional[str] = None
    logVision: Optional[str] = None
    subVision: Optional[str] = None
    ref: Optional[str] = None
    speed: Optional[str] = None
    isLowVision: bool = False
    lowVision: Optional[str] = None


class VisionChartData(BaseModel):
    """电子视力表专用数据"""
    visionType: Optional[str] = None
    spaceType: Optional[str] = None
    environment: Optional[str] = None
    eyeCorrect: Optional[str] = None
    testMode: Optional[str] = None
    openMirror: Optional[bool] = None
    deviceName: Optional[str] = None
    eyes: Optional[EyeData] = None  # 双眼
    od: Optional[EyeData] = None  # 右眼
    os: Optional[EyeData] = None  # 左眼


class BiometerEyeData(BaseModel):
    """单眼生物测量数据"""
    al: Optional[str] = None    # 眼轴长度 Axial Length (mm)
    k1: Optional[str] = None    # 角膜曲率K1 (D)
    k2: Optional[str] = None    # 角膜曲率K2 (D)
    km: Optional[str] = None    # 平均角膜曲率 (D)
    astig: Optional[str] = None # 角膜散光 (D)
    acd: Optional[str] = None   # 前房深度 (mm)
    lt: Optional[str] = None    # 晶状体厚度 (mm)
    wtW: Optional[str] = None   # 白到白距离 (mm)
    snr: Optional[str] = None   # 信噪比


class BiometerData(BaseModel):
    """眼生物测量仪专用数据"""
    od: Optional[BiometerEyeData] = None  # 右眼
    os: Optional[BiometerEyeData] = None  # 左眼
    calculationMode: Optional[str] = None  # 计算模式 (如 SRK/T, Hoffer Q 等)


class VisionScreeningEyeData(BaseModel):
    """单眼视力筛查数据"""
    sph: Optional[str] = None    # 球镜 Sphere (D)
    cyl: Optional[str] = None    # 柱镜 Cylinder (D)
    axis: Optional[str] = None   # 轴位 Axis (deg)
    va: Optional[str] = None     # 视力值 VA
    pupil: Optional[str] = None  # 瞳孔直径 (mm)


class VisionScreeningData(BaseModel):
    """视力筛查仪专用数据"""
    od: Optional[VisionScreeningEyeData] = None
    os: Optional[VisionScreeningEyeData] = None
    pd: Optional[str] = None     # 瞳距 (mm)
    examMode: Optional[str] = None  # 检查模式


class CheckRecord(BaseModel):
    """检查记录 - 统一数据模型"""
    id: str = Field(
        default_factory=lambda: f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    )
    patientInfo: PatientInfo
    metadata: CheckMetadata
    visionChartData: Optional[VisionChartData] = None
    biometerData: Optional[BiometerData] = None
    visionScreeningData: Optional[VisionScreeningData] = None
    rawData: Optional[Dict[str, Any]] = None  # 保存原始数据用于排查
    printed: bool = False
    printTime: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.now)
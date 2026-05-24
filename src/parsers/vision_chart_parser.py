from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.exceptions import DataParseError
from src.core.logger import get_logger
from src.models.data_models import (
    CheckMetadata,
    CheckRecord,
    EyeData,
    PatientInfo,
    VisionChartData,
)

logger = get_logger()


class VisionChartParser:
    @staticmethod
    def parse_http_get(params: Dict[str, Any]) -> CheckRecord:
        try:
            check_time = VisionChartParser._parse_datetime(
                params.get("resultTime", ""),
                ["%Y-%m-%d-%H-%M-%S"]
            )
            left_value = params.get("left") or params.get("f")

            patient_info = PatientInfo(
                patientName=params.get("userName", "未知用户"),
                patientId=params.get("userId") or params.get("userld") or ""
            )

            metadata = CheckMetadata(
                checkTime=check_time,
                deviceType="vision-chart",
                deviceId=params.get("deviceNumber")
            )

            vision_data = VisionChartData(
                visionType=params.get("visionType"),
                spaceType=params.get("spaceType"),
                environment=params.get("environment"),
                eyeCorrect=params.get("eyeCorrect"),
                eyes=VisionChartParser._parse_eye_value(params.get("eyes")),
                od=VisionChartParser._parse_eye_value(params.get("right")),
                os=VisionChartParser._parse_eye_value(left_value)
            )

            record = CheckRecord(
                patientInfo=patient_info,
                metadata=metadata,
                visionChartData=vision_data,
                rawData=params
            )
            logger.info(f"Parsed vision chart: {record.patientInfo.patientName}")
            return record
        except Exception as e:
            logger.error(f"Failed to parse vision chart: {e}")
            raise DataParseError(f"Vision chart parse failed: {e}") from e

    @staticmethod
    def parse_json_object(data: Dict[str, Any]) -> CheckRecord:
        try:
            check_time = VisionChartParser._parse_datetime(
                data.get("DateTime", ""),
                ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d-%H-%M-%S"]
            )
            result = data.get("Result") or {}

            patient_info = PatientInfo(
                patientName=data.get("Name") or "未知用户",
                patientId=data.get("userId") or data.get("patientId") or "",
                phone=data.get("phone") or None,
                birthday=data.get("birthday") or None,
                gender=data.get("gender") or None
            )

            metadata = CheckMetadata(
                checkTime=check_time,
                deviceType="vision-chart",
                deviceId=data.get("DeviceName") or None
            )

            vision_data = VisionChartData(
                visionType=data.get("EyeVersion"),
                spaceType=data.get("SpaceType"),
                environment=data.get("Environment"),
                eyeCorrect=data.get("EyeCorrect"),
                testMode=data.get("TestMode"),
                openMirror=data.get("OpenMirror"),
                deviceName=data.get("DeviceName"),
                od=VisionChartParser._parse_eye_json(result.get("OD")),
                os=VisionChartParser._parse_eye_json(result.get("OS"))
            )

            return CheckRecord(
                patientInfo=patient_info,
                metadata=metadata,
                visionChartData=vision_data,
                rawData=data
            )
        except Exception as e:
            logger.error(f"Failed to parse vision chart JSON: {e}")
            raise DataParseError(f"Vision chart JSON parse failed: {e}") from e

    @staticmethod
    def parse_json_list(items: List[Dict[str, Any]]) -> List[CheckRecord]:
        return [VisionChartParser.parse_json_object(item) for item in items]

    @staticmethod
    def _parse_eye_value(value: Optional[str]) -> EyeData:
        if not value:
            return EyeData()
        value = str(value).strip()
        if not value:
            return EyeData()

        vision = value
        log_vision = ""
        if "(" in value and ")" in value:
            parts = value.split("(", 1)
            vision = parts[0].strip()
            log_vision = parts[1].split(")", 1)[0].strip()
        return EyeData(vision=vision, logVision=log_vision)

    @staticmethod
    def _parse_eye_json(data: Optional[Dict[str, Any]]) -> EyeData:
        if not data:
            return EyeData()
        return EyeData(
            vision=data.get("vision") or None,
            logVision=data.get("logVision") or None,
            subVision=data.get("subVision") or None,
            ref=data.get("ref") or None,
            speed=data.get("speed") or None,
            isLowVision=bool(data.get("isLowVision", False)),
            lowVision=data.get("lowVision") or None
        )

    @staticmethod
    def _parse_datetime(value: Any, formats: List[str]) -> datetime:
        if value:
            text = str(value).strip()
            for fmt in formats:
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            logger.warning(f"Time format parse failed: '{text}', using current time")
        return datetime.now()

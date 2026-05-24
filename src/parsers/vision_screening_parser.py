"""视力筛查仪蓝牙打印数据解析器

设备通过蓝牙SPP发送ESC/POS打印数据流。
系统模拟蓝牙打印机角色，接收数据流并提取结构化数据。

典型视力筛查仪打印格式:
    Name: 张三
    ID: P123456
    Date: 2026-05-23 15:30

    Refraction Results
    ------------------
              S      C      A
    OD    -2.50  -1.00   180
    OS    -2.25  -0.75   175
    PD: 62mm

    VA Results
    ----------
    OD: 1.0   OS: 0.8
"""
from datetime import datetime
from typing import Dict, Any, Optional
import re
from src.models.data_models import (
    PatientInfo, CheckMetadata, VisionScreeningData,
    VisionScreeningEyeData, CheckRecord
)
from src.core.logger import get_logger
from src.core.exceptions import DataParseError

logger = get_logger()


class VisionScreeningParser:
    """视力筛查仪打印数据解析器"""

    @staticmethod
    def parse_escpos_text(text: str) -> CheckRecord:
        """从ESC/POS打印流提取的文本解析视力筛查数据"""
        try:
            patient_info = VisionScreeningParser._extract_patient_info(text)
            check_time = VisionScreeningParser._extract_check_time(text)
            device_id = VisionScreeningParser._extract_device_id(text)
            screening_data = VisionScreeningParser._extract_screening_data(text)

            metadata = CheckMetadata(
                checkTime=check_time,
                deviceType="vision-screening",
                deviceId=device_id
            )

            record = CheckRecord(
                patientInfo=patient_info,
                metadata=metadata,
                visionScreeningData=screening_data,
                rawData={"rawText": text}
            )

            logger.info(f"Parsed vision screening data: {record.patientInfo.patientName}")
            return record

        except Exception as e:
            logger.error(f"Failed to parse vision screening data: {e}")
            raise DataParseError(f"Vision screening parse failed: {e}") from e

    @staticmethod
    def parse_from_dict(data: Dict[str, Any]) -> CheckRecord:
        """从结构化字典解析（用于手动提交/测试）"""
        try:
            patient_info = PatientInfo(
                patientName=data.get("patientName", "未知用户"),
                patientId=data.get("patientId", "")
            )

            metadata = CheckMetadata(
                checkTime=datetime.now(),
                deviceType="vision-screening",
                deviceId=data.get("deviceId")
            )

            od_data = VisionScreeningEyeData(**data.get("od", {}))
            os_data = VisionScreeningEyeData(**data.get("os", {}))
            screening_data = VisionScreeningData(
                od=od_data, os=os_data,
                pd=data.get("pd"),
                examMode=data.get("examMode")
            )

            return CheckRecord(
                patientInfo=patient_info,
                metadata=metadata,
                visionScreeningData=screening_data,
                rawData=data
            )
        except Exception as e:
            logger.error(f"Failed to parse screening dict data: {e}")
            raise DataParseError(f"Screening dict parse failed: {e}") from e

    @staticmethod
    def _extract_patient_info(text: str) -> PatientInfo:
        """提取患者信息"""
        name = "未知用户"
        pid = ""

        name_match = re.search(r'(?:Name|姓名)[:\s]*(\S+)', text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1)

        id_match = re.search(r'(?:Patient\s*ID|ID|编号)[:\s]*(\S+)', text, re.IGNORECASE)
        if id_match:
            pid = id_match.group(1)

        return PatientInfo(patientName=name, patientId=pid)

    @staticmethod
    def _extract_check_time(text: str) -> datetime:
        """提取检查时间"""
        patterns = [
            (r'(?:Date|检查日期|时间)[:\s]*(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}(?::\d{2})?)', '%Y-%m-%d %H:%M:%S'),
            (r'(?:Date|检查日期|时间)[:\s]*(\d{4}[-/]\d{2}[-/]\d{2})', '%Y-%m-%d'),
            (r'(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}(?::\d{2})?)', '%Y-%m-%d %H:%M:%S'),
        ]
        for regex, fmt in patterns:
            m = re.search(regex, text, re.IGNORECASE)
            if m:
                try:
                    return datetime.strptime(m.group(1).replace('/', '-'), fmt)
                except ValueError:
                    continue
        return datetime.now()

    @staticmethod
    def _extract_device_id(text: str) -> Optional[str]:
        """提取设备编号"""
        m = re.search(r'(?:Device\s*SN|Serial|设备编号|SN)[:\s]*(\S+)', text, re.IGNORECASE)
        return m.group(1) if m else None

    @staticmethod
    def _extract_screening_data(text: str) -> VisionScreeningData:
        """从打印文本提取视力筛查数据"""
        od = {"sph": "", "cyl": "", "axis": "", "va": "", "pupil": ""}
        os = {"sph": "", "cyl": "", "axis": "", "va": "", "pupil": ""}

        lines = text.split('\n')

        # 模式1: 表格形式 (S C A 在一行，OD/OS 值在后续行)
        # OD  -2.50  -1.00   180
        # OS  -2.25  -0.75   175
        for line in lines:
            od_match = re.search(
                r'OD?\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\s+(\d+\.?\d*)', line, re.IGNORECASE
            )
            if od_match:
                od["sph"] = od_match.group(1)
                od["cyl"] = od_match.group(2)
                od["axis"] = od_match.group(3)
                continue

            os_match = re.search(
                r'OS?\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\s+(\d+\.?\d*)', line, re.IGNORECASE
            )
            if os_match:
                os["sph"] = os_match.group(1)
                os["cyl"] = os_match.group(2)
                os["axis"] = os_match.group(3)
                continue

            # Right eye labeled
            right_match = re.search(
                r'(?:Right|R|右眼).*?S\s*[:=]?\s*([-+]?\d+\.?\d*).*?C\s*[:=]?\s*([-+]?\d+\.?\d*).*?A\s*[:=]?\s*(\d+\.?\d*)',
                line, re.IGNORECASE
            )
            if right_match:
                od["sph"] = right_match.group(1)
                od["cyl"] = right_match.group(2)
                od["axis"] = right_match.group(3)
                continue

            # Left eye labeled
            left_match = re.search(
                r'(?:Left|L|左眼).*?S\s*[:=]?\s*([-+]?\d+\.?\d*).*?C\s*[:=]?\s*([-+]?\d+\.?\d*).*?A\s*[:=]?\s*(\d+\.?\d*)',
                line, re.IGNORECASE
            )
            if left_match:
                os["sph"] = left_match.group(1)
                os["cyl"] = left_match.group(2)
                os["axis"] = left_match.group(3)

        # 提取 VA (视力值)
        va_od = re.search(r'(?:VA|视力).*?OD\s*[=:]?\s*([\d.]+)', text, re.IGNORECASE)
        if va_od:
            od["va"] = va_od.group(1)
        va_os = re.search(r'(?:VA|视力).*?OS\s*[=:]?\s*([\d.]+)', text, re.IGNORECASE)
        if va_os:
            os["va"] = va_os.group(1)

        # 提取 PD (瞳距)
        pd_val = "62"
        pd_match = re.search(r'PD\s*[=:]?\s*(\d+\.?\d*)\s*(?:mm)?', text, re.IGNORECASE)
        if pd_match:
            pd_val = pd_match.group(1)

        # 检查模式
        exam_mode = None
        mode_match = re.search(r'(?:Mode|检查模式)[:\s]*(\S+)', text, re.IGNORECASE)
        if mode_match:
            exam_mode = mode_match.group(1)

        return VisionScreeningData(
            od=VisionScreeningEyeData(**od) if any(od.values()) else None,
            os=VisionScreeningEyeData(**os) if any(os.values()) else None,
            pd=pd_val,
            examMode=exam_mode,
        )

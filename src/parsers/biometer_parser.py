"""眼生物测量仪蓝牙打印数据解析器

设备通过蓝牙SPP发送ESC/POS打印数据流。
系统模拟蓝牙打印机角色，接收数据流并提取结构化数据。

典型生物测量仪打印格式（英文/中文混合）:
    Patient ID: P123456
    Name: 张三
    Exam Date: 2026-05-23 15:30

    Measurement Results
    -------------------
              OD        OS
    AL(mm)   23.45     23.50
    K1(D)    42.50     43.00
    K2(D)    44.00     44.50
    ACD(mm)  3.20      3.15
    LT(mm)   4.10      4.05
    WTW(mm)  11.8      11.9
"""
from datetime import datetime
from typing import Dict, Any, Optional
import re
from src.models.data_models import (
    PatientInfo, CheckMetadata, BiometerData, BiometerEyeData, CheckRecord
)
from src.core.logger import get_logger
from src.core.exceptions import DataParseError

logger = get_logger()


# 字段名正则映射
BIOMETER_FIELD_PATTERNS = {
    'al':   r'AL|Axial\s*Length|眼轴(长度)?',
    'k1':   r'K1|R1',
    'k2':   r'K2|R2',
    'astig': r'AST|Astig|CYL|散光',
    'km':   r'K\s*m|Km|Avg\s*K|平均',
    'acd':  r'ACD|Anterior\s*Chamber|前房(深度)?',
    'lt':   r'LT|Lens\s*Thick|晶体|晶状体',
    'wtW':  r'WTW|W-W|WtW|白到白',
    'snr':  r'SNR|信噪比',
}


class BiometerParser:
    """眼生物测量仪打印数据解析器"""

    @staticmethod
    def parse_escpos_text(text: str) -> CheckRecord:
        """从ESC/POS打印流提取的文本解析生物测量数据"""
        try:
            patient_info = BiometerParser._extract_patient_info(text)
            check_time = BiometerParser._extract_check_time(text)
            device_id = BiometerParser._extract_device_id(text)
            biometer_data = BiometerParser._extract_biometer_data(text)

            metadata = CheckMetadata(
                checkTime=check_time,
                deviceType="biometer",
                deviceId=device_id
            )

            record = CheckRecord(
                patientInfo=patient_info,
                metadata=metadata,
                biometerData=biometer_data,
                rawData={"rawText": text}
            )

            logger.info(f"Parsed biometer data: {record.patientInfo.patientName}")
            return record

        except Exception as e:
            logger.error(f"Failed to parse biometer data: {e}")
            raise DataParseError(f"Biometer data parse failed: {e}") from e

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
                deviceType="biometer",
                deviceId=data.get("deviceId")
            )

            od_data = BiometerEyeData(**data.get("od", {}))
            os_data = BiometerEyeData(**data.get("os", {}))
            biometer_data = BiometerData(od=od_data, os=os_data,
                                         calculationMode=data.get("calculationMode"))

            return CheckRecord(
                patientInfo=patient_info,
                metadata=metadata,
                biometerData=biometer_data,
                rawData=data
            )
        except Exception as e:
            logger.error(f"Failed to parse biometer dict data: {e}")
            raise DataParseError(f"Biometer dict parse failed: {e}") from e

    @staticmethod
    def _extract_patient_info(text: str) -> PatientInfo:
        """提取患者信息"""
        name = "未知用户"
        pid = ""

        name_match = re.search(r'(?:Name|姓名)[:\s]*(\S+)', text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1)

        id_match = re.search(r'(?:Patient\s*ID|患者ID|ID)[:\s]*(\S+)', text, re.IGNORECASE)
        if id_match:
            pid = id_match.group(1)

        return PatientInfo(patientName=name, patientId=pid)

    @staticmethod
    def _extract_check_time(text: str) -> datetime:
        """提取检查时间"""
        patterns = [
            (r'(?:Exam\s*Date|Date|检查日期|时间)[:\s]*(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}(?::\d{2})?)', '%Y-%m-%d %H:%M:%S'),
            (r'(?:Exam\s*Date|Date|检查日期|时间)[:\s]*(\d{4}[-/]\d{2}[-/]\d{2})', '%Y-%m-%d'),
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
    def _extract_biometer_data(text: str) -> BiometerData:
        """提取生物测量数据（从表中解析 OD/OS 列）"""
        od = {}
        os = {}

        lines = text.split('\n')
        for line in lines:
            for field, pattern in BIOMETER_FIELD_PATTERNS.items():
                match = re.search(pattern + r'\s*[\s:]+\s*([\d.]+)\s+([\d.]+)', line, re.IGNORECASE)
                if match:
                    od[field] = match.group(1)
                    os[field] = match.group(2)
                    break
                # Try single value pattern (only one eye)
                match2 = re.search(pattern + r'\s*[\s:]+\s*([\d.]+)', line, re.IGNORECASE)
                if match2 and field not in od:
                    od[field] = match2.group(1)
                    break

        calc_mode = None
        mode_match = re.search(r'(?:Formula|Mode|计算模式)[:\s]*(\S+)', text, re.IGNORECASE)
        if mode_match:
            calc_mode = mode_match.group(1)

        return BiometerData(
            od=BiometerEyeData(**od) if od else None,
            os=BiometerEyeData(**os) if os else None,
            calculationMode=calc_mode
        )

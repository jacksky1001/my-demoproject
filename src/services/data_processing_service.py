from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

import requests

from src.models.data_models import CheckRecord
from src.core.logger import get_logger
from src.core.exceptions import DataParseError
from src.parsers.biometer_parser import BiometerParser
from src.parsers.vision_chart_parser import VisionChartParser
from src.parsers.vision_screening_parser import VisionScreeningParser

logger = get_logger()


class DataProcessingService:
    """数据处理服务 - 解析设备数据并转换为统一格式"""

    @staticmethod
    def parse_vision_chart_http(params: Dict[str, Any]) -> CheckRecord:
        """解析电子视力表HTTP回调数据 - PRD REQ-001a"""
        return VisionChartParser.parse_http_get(params)

    @staticmethod
    def parse_vision_chart_json_object(data: Dict[str, Any]) -> CheckRecord:
        """解析电子视力表主动拉取JSON数据"""
        return VisionChartParser.parse_json_object(data)

    @staticmethod
    def parse_vision_chart_json_list(items: List[Dict[str, Any]]) -> List[CheckRecord]:
        """解析电子视力表主动拉取JSON数组"""
        return VisionChartParser.parse_json_list(items)

    @staticmethod
    def fetch_vision_chart_pull(
        ip: str,
        port: int = 8181,
        mode: str = "latest",
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[CheckRecord]:
        """从电子视力表设备主动拉取检查结果"""
        if not ip:
            raise DataParseError("Vision chart device IP is required")

        try:
            base_url = f"http://{ip}:{port}"
            if mode == "json":
                query = urlencode({k: v for k, v in {"start": start, "end": end}.items() if v})
                url = f"{base_url}/json"
                if query:
                    url = f"{url}?{query}"
            else:
                url = base_url

            response = requests.get(url, timeout=5)
            response.raise_for_status()
            payload = response.json()

            if isinstance(payload, list):
                return VisionChartParser.parse_json_list(payload)
            if isinstance(payload, dict) and "Result" in payload:
                return [VisionChartParser.parse_json_object(payload)]

            raise DataParseError("Unsupported vision chart response format")
        except requests.RequestException as e:
            raise DataParseError(f"Vision chart pull request failed: {e}") from e

    @staticmethod
    def parse_biometer_escpos(text: str) -> CheckRecord:
        """解析眼生物测量仪蓝牙打印数据"""
        return BiometerParser.parse_escpos_text(text)

    @staticmethod
    def parse_biometer_dict(data: Dict[str, Any]) -> CheckRecord:
        """从字典解析眼生物测量仪数据（手动测试用）"""
        return BiometerParser.parse_from_dict(data)

    @staticmethod
    def parse_vision_screening_escpos(text: str) -> CheckRecord:
        """解析视力筛查仪蓝牙打印数据"""
        return VisionScreeningParser.parse_escpos_text(text)

    @staticmethod
    def parse_vision_screening_dict(data: Dict[str, Any]) -> CheckRecord:
        """从字典解析视力筛查仪数据（手动测试用）"""
        return VisionScreeningParser.parse_from_dict(data)
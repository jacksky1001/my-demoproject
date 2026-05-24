from typing import List
from datetime import datetime
import json
from src.models.data_models import CheckRecord, EyeData
from src.drivers.escpos_commands import ESCPOSCommands
from src.core.logger import get_logger

logger = get_logger()


class PrintTemplate56mm:
    """56mm 热敏打印机模板"""

    def __init__(self):
        self.cmd = ESCPOSCommands()

    def generate_vision_chart_report(self, record: CheckRecord) -> List[bytes]:
        """生成电子视力表报告 - 56mm宽度"""
        commands = []

        # 1. 初始化
        commands.append(self.cmd.initialize())

        # 2. 标题 - 居中放大
        commands.append(self.cmd.align_center())
        commands.append(self.cmd.set_font_size(width_mult=1, height_mult=1))
        commands.append(self.cmd.set_bold(True))
        commands.append(self.cmd.text("视力中心\n"))
        commands.append(self.cmd.text("视力检查报告\n"))
        commands.append(self.cmd.set_bold(False))
        commands.append(self.cmd.set_font_size())  # 恢复标准大小
        commands.append(self.cmd.line_feed(1))

        # 3. 患者信息 - 左对齐
        commands.append(self.cmd.align_left())
        commands.append(self.cmd.text(f"姓名: {record.patientInfo.patientName}\n"))
        commands.append(self.cmd.text(f"ID: {record.patientInfo.patientId}\n"))
        commands.append(self.cmd.text(f"时间: {record.metadata.checkTime.strftime('%Y-%m-%d %H:%M')}\n"))
        device_name = record.visionChartData.deviceName if record.visionChartData else None
        commands.append(self.cmd.text(f"设备: {device_name or record.metadata.deviceId or '电子视力表'}\n"))

        # 4. 分隔线
        commands.append(self.cmd.text("-" * 20 + "\n"))

        # 5. 视力数据
        if record.visionChartData:
            data = record.visionChartData
            commands.append(self.cmd.set_bold(True))
            commands.append(self.cmd.text("      右眼    左眼\n"))
            commands.append(self.cmd.set_bold(False))

            od = data.od or EyeData()
            os = data.os or EyeData()
            commands.append(self.cmd.text(f"裸眼: {od.vision or '-':<6}  {os.vision or '-':<6}\n"))
            if od.logVision or os.logVision:
                commands.append(self.cmd.text(f"对数: {od.logVision or '-':<6}  {os.logVision or '-':<6}\n"))
            if od.ref or os.ref:
                commands.append(self.cmd.text(f"参考: {od.ref or '-':<6}  {os.ref or '-':<6}\n"))
            if od.speed or os.speed:
                commands.append(self.cmd.text(f"用时: {od.speed or '-':<6}  {os.speed or '-':<6}\n"))
            if od.lowVision or os.lowVision:
                commands.append(self.cmd.text(f"低视: {od.lowVision or '-':<6}  {os.lowVision or '-':<6}\n"))

            if data.eyeCorrect:
                commands.append(self.cmd.text(f"矫正: {data.eyeCorrect}\n"))
            if data.visionType:
                commands.append(self.cmd.text(f"视标: {data.visionType}\n"))
            if data.spaceType:
                commands.append(self.cmd.text(f"距离: {data.spaceType}\n"))
            #if data.testMode:
            #    commands.append(self.cmd.text(f"模式: {data.testMode}\n"))

        commands.append(self.cmd.line_feed(1))

        # 6. 二维码 - 居中，适合56mm纸张的尺寸
        commands.append(self.cmd.align_center())
        qr_data = self._generate_qr_json(record)
        commands.extend(self.cmd.print_qr_full(qr_data, module_size=6, level="M"))
        commands.append(self.cmd.line_feed(1))
        commands.append(self.cmd.text("扫码查看完整数据\n"))

        # 7. 结尾走纸切纸
        commands.append(self.cmd.line_feed(3))
        commands.append(self.cmd.cut_paper(full_cut=True))

        return commands

    def _generate_qr_json(self, record: CheckRecord) -> str:
        """生成完整业务数据二维码JSON"""
        qr_dict = {
            # "v": "1",
            #"g": datetime.now().strftime("%Y%m%d%H%M%S"),
            #"p": {
                #"n": record.patientInfo.patientName,
                #"id": record.patientInfo.patientId,
                #"ph": record.patientInfo.phone or "",
                #"bd": record.patientInfo.birthday or "",
                #"sex": record.patientInfo.gender or ""
            #},
            "c": {
                #"rid": record.id,
                "dt": record.metadata.deviceType,
                #"did": record.metadata.deviceId or "",
                #"t": record.metadata.checkTime.strftime("%Y%m%d%H%M%S"),
                "data": self._get_complete_business_data(record)
            }
        }
        qr_text = json.dumps(qr_dict, ensure_ascii=False, separators=(",", ":"))
        logger.info(f"二维码内容长度: {len(qr_text.encode('utf-8'))} bytes, module_size=6, level=M")
        return qr_text

    def _get_complete_business_data(self, record: CheckRecord) -> dict:
        if record.visionChartData:
            data = record.visionChartData
            od = data.od or EyeData()
            os = data.os or EyeData()
            return {
                "vt": data.visionType or "",
                "st": data.spaceType or "",
                #"env": data.environment or "",
                "ec": data.eyeCorrect or "",
                #"tm": data.testMode or "",
                #"om": data.openMirror,
                "dn": data.deviceName or "",
                "od": self._eye_data(od),
                "os": self._eye_data(os)
            }
        if record.biometerData:
            data = record.biometerData
            return {
                "od": self._biometer_eye_data(data.od),
                "os": self._biometer_eye_data(data.os),
                "cm": data.calculationMode or ""
            }
        if record.visionScreeningData:
            data = record.visionScreeningData
            return {
                "od": self._screening_eye_data(data.od),
                "os": self._screening_eye_data(data.os),
                "pd": data.pd or "",
                "em": data.examMode or ""
            }
        return record.rawData or {}

    def _eye_data(self, eye: EyeData) -> dict:
        return {
            "v": eye.vision or "",
            "lv": eye.logVision or "",
            "sv": eye.subVision or "",
            "ref": eye.ref or "",
            "sp": eye.speed or "",
            "low": eye.isLowVision,
            "lowv": eye.lowVision or ""
        }

    def _biometer_eye_data(self, eye) -> dict:
        if not eye:
            return {}
        return {
            "al": eye.al or "",
            "k1": eye.k1 or "",
            "k2": eye.k2 or "",
            "km": eye.km or "",
            "ast": eye.astig or "",
            "acd": eye.acd or "",
            "lt": eye.lt or "",
            "wtw": eye.wtW or "",
            "snr": eye.snr or ""
        }

    def _screening_eye_data(self, eye) -> dict:
        if not eye:
            return {}
        return {
            "s": eye.sph or "",
            "c": eye.cyl or "",
            "a": eye.axis or "",
            "va": eye.va or "",
            "p": eye.pupil or ""
        }

    def generate_biometer_report(self, record: CheckRecord) -> List[bytes]:
        """生成眼生物测量仪报告 - 56mm宽度"""
        commands = []
        commands.append(self.cmd.initialize())
        commands.append(self.cmd.align_center())
        commands.append(self.cmd.set_font_size(width_mult=1, height_mult=1))
        commands.append(self.cmd.set_bold(True))
        commands.append(self.cmd.text("视力中心\n"))
        commands.append(self.cmd.text("生物测量报告\n"))
        commands.append(self.cmd.set_bold(False))
        commands.append(self.cmd.set_font_size())
        commands.append(self.cmd.line_feed(1))

        commands.append(self.cmd.align_left())
        commands.append(self.cmd.text(f"姓名: {record.patientInfo.patientName}\n"))
        commands.append(self.cmd.text(f"ID: {record.patientInfo.patientId}\n"))
        commands.append(self.cmd.text(f"时间: {record.metadata.checkTime.strftime('%Y-%m-%d %H:%M')}\n"))
        commands.append(self.cmd.text(f"设备: 眼生物测量仪\n"))
        commands.append(self.cmd.text("-" * 20 + "\n"))

        if record.biometerData:
            bd = record.biometerData
            commands.append(self.cmd.set_bold(True))
            commands.append(self.cmd.text("         右眼(OD)  左眼(OS)\n"))
            commands.append(self.cmd.set_bold(False))

            od = bd.od
            os = bd.os
            if od and os:
                if od.al or os.al:
                    commands.append(self.cmd.text(f"AL(mm):  {od.al or '-':<8} {os.al or '-':<8}\n"))
                if od.k1 or os.k1:
                    commands.append(self.cmd.text(f"K1(D):   {od.k1 or '-':<8} {os.k1 or '-':<8}\n"))
                if od.k2 or os.k2:
                    commands.append(self.cmd.text(f"K2(D):   {od.k2 or '-':<8} {os.k2 or '-':<8}\n"))
                if od.acd or os.acd:
                    commands.append(self.cmd.text(f"ACD(mm): {od.acd or '-':<8} {os.acd or '-':<8}\n"))

        commands.append(self.cmd.line_feed(1))
        commands.append(self.cmd.align_center())
        qr_data = self._generate_qr_json(record)
        commands.extend(self.cmd.print_qr_full(qr_data, module_size=4, level="M"))
        commands.append(self.cmd.line_feed(1))
        commands.append(self.cmd.text("扫码查看完整数据\n"))
        commands.append(self.cmd.line_feed(3))
        commands.append(self.cmd.cut_paper(full_cut=True))
        return commands

    def generate_vision_screening_report(self, record: CheckRecord) -> List[bytes]:
        """生成视力筛查仪报告 - 56mm宽度"""
        commands = []
        commands.append(self.cmd.initialize())
        commands.append(self.cmd.align_center())
        commands.append(self.cmd.set_font_size(width_mult=1, height_mult=1))
        commands.append(self.cmd.set_bold(True))
        commands.append(self.cmd.text("视力中心\n"))
        commands.append(self.cmd.text("视力筛查报告\n"))
        commands.append(self.cmd.set_bold(False))
        commands.append(self.cmd.set_font_size())
        commands.append(self.cmd.line_feed(1))

        commands.append(self.cmd.align_left())
        commands.append(self.cmd.text(f"姓名: {record.patientInfo.patientName}\n"))
        commands.append(self.cmd.text(f"ID: {record.patientInfo.patientId}\n"))
        commands.append(self.cmd.text(f"时间: {record.metadata.checkTime.strftime('%Y-%m-%d %H:%M')}\n"))
        commands.append(self.cmd.text(f"设备: 视力筛查仪\n"))
        commands.append(self.cmd.text("-" * 20 + "\n"))

        if record.visionScreeningData:
            sd = record.visionScreeningData
            commands.append(self.cmd.set_bold(True))
            commands.append(self.cmd.text("      S       C       A\n"))
            commands.append(self.cmd.set_bold(False))

            od = sd.od
            os = sd.os
            if od:
                commands.append(self.cmd.text(f"OD: {od.sph or '-':<7} {od.cyl or '-':<7} {od.axis or '-':<7}\n"))
            if os:
                commands.append(self.cmd.text(f"OS: {os.sph or '-':<7} {os.cyl or '-':<7} {os.axis or '-':<7}\n"))
            if sd.pd:
                commands.append(self.cmd.text(f"PD: {sd.pd}mm\n"))

        commands.append(self.cmd.line_feed(1))
        commands.append(self.cmd.align_center())
        qr_data = self._generate_qr_json(record)
        commands.extend(self.cmd.print_qr_full(qr_data, module_size=4, level="M"))
        commands.append(self.cmd.line_feed(1))
        commands.append(self.cmd.text("扫码查看完整数据\n"))
        commands.append(self.cmd.line_feed(3))
        commands.append(self.cmd.cut_paper(full_cut=True))
        return commands
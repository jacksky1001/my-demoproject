from typing import Optional
from datetime import datetime
from src.models.data_models import CheckRecord
from src.drivers.printer_driver import PrinterDriver, SimulatedPrinterDriver
from src.templates.print_templates import PrintTemplate56mm
from src.core.config import get_config
from src.core.logger import get_logger
from src.core.exceptions import PrintError

logger = get_logger()


class PrintingService:
    """打印服务 - 处理打印业务逻辑"""

    def __init__(self):
        self.config = get_config()
        self.driver: Optional[PrinterDriver] = None
        self.template = PrintTemplate56mm()
        self._init_driver()

    def _init_driver(self):
        """初始化打印机驱动"""
        if self.config.printer.simulate:
            logger.info("🖨️ 使用模拟打印机")
            self.driver = SimulatedPrinterDriver()
        else:
            logger.warning("⚠️ 蓝牙打印机暂未实现，使用模拟模式")
            self.driver = SimulatedPrinterDriver()  # 阶段2切换

    def print_record(self, record: CheckRecord, force: bool = None) -> bool:
        """打印一条检查记录
        force: True=强制打印, False=跳过, None=根据配置
        """
        should_print = force if force is not None else self.config.printer.auto_print

        if not should_print:
            logger.info(f"⏭️ 跳过自动打印: {record.patientInfo.patientName}")
            return False

        try:
            # 根据设备类型选择模板
            if record.metadata.deviceType == "vision-chart":
                commands = self.template.generate_vision_chart_report(record)
            elif record.metadata.deviceType == "biometer":
                commands = self.template.generate_biometer_report(record)
            elif record.metadata.deviceType == "vision-screening":
                commands = self.template.generate_vision_screening_report(record)
            else:
                logger.warning(f"❓ 未支持的设备类型: {record.metadata.deviceType}")
                return False

            # 发送到打印机
            success = self.driver.print_commands(commands)

            if success:
                record.printed = True
                record.printTime = datetime.now()
                logger.info(f"✅ 打印成功: {record.patientInfo.patientName}")

            return success

        except Exception as e:
            logger.error(f"❌ 打印失败: {e}")
            raise PrintError(f"打印失败: {e}") from e

    def test_print(self) -> bool:
        """打印测试页"""
        commands = [
            self.template.cmd.initialize(),
            self.template.cmd.align_center(),
            self.template.cmd.set_bold(True),
            self.template.cmd.text("=== 测试页 ==="),
            self.template.cmd.set_bold(False),
            self.template.cmd.line_feed(1),
            self.template.cmd.text(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
            self.template.cmd.text(f"模式: {'模拟打印' if self.config.printer.simulate else '蓝牙打印'}"),
            self.template.cmd.line_feed(3),
            self.template.cmd.cut_paper()
        ]
        return self.driver.print_commands(commands)

    def set_printer_driver(self, driver: PrinterDriver):
        """动态设置打印机驱动"""
        if self.driver:
            try:
                self.driver.disconnect()
            except:
                pass
        self.driver = driver
        logger.info(f"🖨️ 打印机驱动已切换: {driver.__class__.__name__}")
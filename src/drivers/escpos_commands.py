from typing import List


class ESCPOSCommands:
    """ESC/POS 命令封装 - 禁止魔法数字！"""

    # 常用编码
    ENCODING_GBK = "gbk"
    ENCODING_GB18030 = "gb18030"
    ENCODING_UTF8 = "utf-8"

    @staticmethod
    def initialize() -> bytes:
        """初始化打印机"""
        return b"\x1b\x40"  # ESC @

    @staticmethod
    def align_left() -> bytes:
        """左对齐"""
        return b"\x1b\x61\x00"  # ESC a 0

    @staticmethod
    def align_center() -> bytes:
        """居中对齐"""
        return b"\x1b\x61\x01"  # ESC a 1

    @staticmethod
    def align_right() -> bytes:
        """右对齐"""
        return b"\x1b\x61\x02"  # ESC a 2

    @staticmethod
    def set_bold(enabled: bool = True) -> bytes:
        """设置/取消加粗"""
        return b"\x1b\x45\x01" if enabled else b"\x1b\x45\x00"

    @staticmethod
    def set_font_size(width_mult: int = 0, height_mult: int = 0) -> bytes:
        """设置字体大小
        width_mult: 0-7 (1-8倍宽)
        height_mult: 0-7 (1-8倍高)
        """
        param = (width_mult & 0x07) | ((height_mult & 0x07) << 4)
        return b"\x1d\x21" + bytes([param])  # GS ! n

    @staticmethod
    def line_feed(lines: int = 1) -> bytes:
        """换行"""
        return b"\x0a" * lines

    @staticmethod
    def text(content: str, encoding: str = "gbk") -> bytes:
        """输出文本 - 中文打印机通常用GBK"""
        return content.encode(encoding, errors="replace")

    @staticmethod
    def set_qr_size(module_size: int = 6) -> bytes:
        """设置二维码模块大小 (1-16)"""
        return b"\x1d\x28\x6b\x03\x00\x31\x43" + bytes([module_size])

    @staticmethod
    def set_qr_error_correction(level: str = "M") -> bytes:
        """设置二维码纠错等级
        level: L(7%), M(15%, 默认), Q(25%), H(30%)
        """
        level_map = {"L": 48, "M": 49, "Q": 50, "H": 51}
        return b"\x1d\x28\x6b\x03\x00\x31\x45" + bytes([level_map[level]])

    @staticmethod
    def store_qr_data(data: str) -> bytes:
        """存储二维码数据"""
        encoded = data.encode("utf-8")
        data_len = len(encoded)
        total_len = data_len + 3
        pL = total_len % 256
        pH = total_len // 256
        return b"\x1d\x28\x6b" + bytes([pL, pH, 49, 80, 48]) + encoded

    @staticmethod
    def print_qr() -> bytes:
        """打印已存储的二维码"""
        return b"\x1d\x28\x6b\x03\x00\x31\x51\x30"

    @classmethod
    def print_qr_full(cls, data: str, module_size: int = 6, level: str = "M") -> List[bytes]:
        """完整的二维码打印流程"""
        return [
            cls.set_qr_size(module_size),
            cls.set_qr_error_correction(level),
            cls.store_qr_data(data),
            cls.print_qr()
        ]

    @staticmethod
    def cut_paper(full_cut: bool = True) -> bytes:
        """切纸"""
        return b"\x1d\x56\x41\x00" if full_cut else b"\x1d\x56\x42\x00"
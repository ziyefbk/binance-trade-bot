"""
日志系统
TODO: Agent 6 实现
"""

import logging
from logging.handlers import RotatingFileHandler


class TradingLogger:
    """交易日志系统"""

    def __init__(self, log_file: str = "logs/trading.log"):
        """
        初始化日志系统

        Args:
            log_file: 日志文件路径
        """
        self.logger = logging.getLogger("BinanceArbitrageBot")
        self.logger.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 文件处理器（自动轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)

        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def info(self, msg: str):
        """记录信息"""
        self.logger.info(msg)

    def error(self, msg: str):
        """记录错误"""
        self.logger.error(msg)

    def warning(self, msg: str):
        """记录警告"""
        self.logger.warning(msg)

    def debug(self, msg: str):
        """记录调试信息"""
        self.logger.debug(msg)

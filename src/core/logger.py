"""日志系统"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from src.core.config import ConfigManager


class LoggerManager:
    """日志管理器"""

    _instance: Optional["LoggerManager"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls, config: Optional[ConfigManager] = None):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: Optional[ConfigManager] = None):
        """初始化日志管理器"""
        if self._initialized:
            return

        self.config = config or ConfigManager()
        self._setup_logger()
        self._initialized = True

    def _setup_logger(self):
        """设置日志"""
        LoggerManager._logger = logging.getLogger("ai_windbg")
        
        # 如果启用了调试模式，使用 DEBUG 级别
        log_level = "DEBUG" if self.config.is_debug() else self.config.get_log_level()
        LoggerManager._logger.setLevel(getattr(logging, log_level))

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        LoggerManager._logger.addHandler(console_handler)

        # 文件处理器
        log_file = self.config.get_log_file()
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.get("logging.max_size", 10485760),
            backupCount=self.config.get("logging.backup_count", 5),
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        LoggerManager._logger.addHandler(file_handler)

    @classmethod
    def get_logger(cls, config: Optional[ConfigManager] = None) -> logging.Logger:
        """获取日志实例"""
        if cls._logger is None:
            cls(config)
        return cls._logger

    @classmethod
    def debug(cls, message: str):
        """记录调试信息"""
        cls.get_logger().debug(message)

    @classmethod
    def info(cls, message: str):
        """记录信息"""
        cls.get_logger().info(message)

    @classmethod
    def warning(cls, message: str):
        """记录警告"""
        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message: str, exc_info: bool = False):
        """记录错误"""
        cls.get_logger().error(message, exc_info=exc_info)

    @classmethod
    def critical(cls, message: str, exc_info: bool = False):
        """记录严重错误"""
        cls.get_logger().critical(message, exc_info=exc_info)

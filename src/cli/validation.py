"""输入验证器"""

import os
from pathlib import Path
from typing import Tuple, Optional

from src.core.logger import LoggerManager
from src.core.exceptions import InputValidationError


class InputValidator:
    """输入验证器"""

    @staticmethod
    def validate_filepath(path: str) -> Tuple[bool, str]:
        """验证文件路径"""
        if not path or path.strip() == "":
            return False, "路径不能为空"

        if not os.path.exists(path):
            return False, "文件不存在"

        if not path.endswith('.dmp'):
            return False, "必须是 .dmp 文件"

        return True, "验证通过"

    @staticmethod
    def validate_command(command: str) -> Tuple[bool, str]:
        """验证命令"""
        if not command or command.strip() == "":
            return False, "命令不能为空"

        if len(command) > 1000:
            return False, "命令过长"

        return True, "验证通过"

    @staticmethod
    def validate_memory_address(address: str) -> Tuple[bool, str]:
        """验证内存地址"""
        try:
            int(address, 16)
            return True, "验证通过"
        except ValueError:
            return False, "无效的内存地址格式"

    @staticmethod
    def validate_mode(mode: str) -> Tuple[bool, str]:
        """验证显示模式"""
        valid_modes = ["raw", "smart", "both"]
        if mode.lower() in valid_modes:
            return True, "验证通过"
        return False, f"无效的模式，可用模式: {', '.join(valid_modes)}"

    @staticmethod
    def sanitize_command(command: str) -> str:
        """清理命令，移除危险字符"""
        dangerous_chars = [';', '|', '&', '`', '$', '(', ')', '<', '>']
        for char in dangerous_chars:
            if char in command and not command.startswith('.'):
                LoggerManager.warning(f"检测到潜在危险字符: {char}")
        return command.strip()

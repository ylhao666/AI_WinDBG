"""WinDBG 引擎封装"""

import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.core.config import ConfigManager
from src.core.logger import LoggerManager
from src.core.exceptions import WinDBGError, DumpLoadError, CommandExecutionError


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    output: str
    error: str = ""
    exit_code: int = 0
    command: str = ""


class WinDBGEngine:
    """WinDBG 调试引擎封装类"""

    def __init__(self, config: Optional[ConfigManager] = None):
        """初始化 WinDBG 引擎"""
        self.config = config or ConfigManager()
        self.windbg_path = self._get_windbg_path()
        self.symbol_path = self.config.get_symbol_path()
        self.timeout = self.config.get_windbg_timeout()
        self.current_dump: Optional[str] = None
        self._check_availability()

    def _get_windbg_path(self) -> str:
        """获取 WinDBG 路径"""
        path = self.config.get_windbg_path()

        # 如果配置的路径存在，直接使用
        if Path(path).exists():
            return path

        # 尝试在 PATH 中查找
        for search_path in os.environ["PATH"].split(os.pathsep):
            full_path = Path(search_path) / "cdb.exe"
            if full_path.exists():
                return str(full_path)

        # 尝试常见的安装路径
        common_paths = [
            "C:\\Program Files (x86)\\Windows Kits\\10\\Debuggers\\x64\\cdb.exe",
            "C:\\Program Files\\Windows Kits\\10\\Debuggers\\x64\\cdb.exe",
            "C:\\Program Files (x86)\\Windows Kits\\8.1\\Debuggers\\x64\\cdb.exe",
        ]

        for common_path in common_paths:
            if Path(common_path).exists():
                return common_path

        return "cdb.exe"

    def _check_availability(self):
        """检查 WinDBG 是否可用"""
        try:
            result = subprocess.run(
                [self.windbg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                LoggerManager.info(f"WinDBG 引擎已就绪: {self.windbg_path}")
            else:
                LoggerManager.warning(f"WinDBG 版本检查失败: {result.stderr}")
        except FileNotFoundError:
            LoggerManager.error(f"未找到 WinDBG: {self.windbg_path}")
        except Exception as e:
            LoggerManager.warning(f"WinDBG 可用性检查失败: {str(e)}")

    def load_dump(self, dump_path: str) -> bool:
        """加载崩溃转储文件"""
        if not Path(dump_path).exists():
            raise DumpLoadError(f"转储文件不存在: {dump_path}")

        if not dump_path.endswith('.dmp'):
            raise DumpLoadError("文件扩展名必须是 .dmp")

        try:
            # 测试加载转储文件
            test_command = f'-z "{dump_path}" -c "q"'
            result = subprocess.run(
                [self.windbg_path] + test_command.split(),
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                self.current_dump = dump_path
                LoggerManager.info(f"成功加载转储文件: {dump_path}")
                return True
            else:
                raise DumpLoadError(f"加载转储文件失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise DumpLoadError("加载转储文件超时")
        except Exception as e:
            raise DumpLoadError(f"加载转储文件时发生错误: {str(e)}")

    def execute_command(self, command: str) -> CommandResult:
        """执行 WinDBG 命令"""
        if not self.current_dump:
            raise CommandExecutionError("未加载转储文件")

        try:
            # 构建完整命令
            full_command = f'-z "{self.current_dump}" -c "{command};q"'

            LoggerManager.debug(f"执行 WinDBG 命令: {command}")

            result = subprocess.run(
                [self.windbg_path] + full_command.split(),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore'
            )

            command_result = CommandResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                command=command
            )

            if command_result.success:
                LoggerManager.debug(f"命令执行成功，输出长度: {len(command_result.output)}")
            else:
                LoggerManager.warning(f"命令执行失败: {command_result.error}")

            return command_result

        except subprocess.TimeoutExpired:
            raise CommandExecutionError("命令执行超时")
        except Exception as e:
            raise CommandExecutionError(f"执行命令时发生错误: {str(e)}")

    def get_session_info(self) -> Dict[str, Any]:
        """获取当前会话信息"""
        return {
            "windbg_path": self.windbg_path,
            "symbol_path": self.symbol_path,
            "current_dump": self.current_dump,
            "timeout": self.timeout
        }

    def close(self):
        """关闭调试会话"""
        self.current_dump = None
        LoggerManager.info("WinDBG 会话已关闭")

    def is_available(self) -> bool:
        """检查 WinDBG 是否可用"""
        return Path(self.windbg_path).exists()

    def is_dump_loaded(self) -> bool:
        """检查是否已加载转储文件"""
        return self.current_dump is not None

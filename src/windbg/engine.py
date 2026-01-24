"""WinDBG 引擎封装"""

import subprocess
import os
import threading
import queue
import time
import re
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
        
        # 持久会话相关
        self._process: Optional[subprocess.Popen] = None
        self._output_queue: queue.Queue = queue.Queue()
        self._output_thread: Optional[threading.Thread] = None
        self._is_running = False
        self._lock = threading.Lock()
        # 输出回调函数
        self._output_callback: Optional[callable] = None
        
        self._check_availability()

    def set_output_callback(self, callback: Optional[callable]):
        """设置输出回调函数，用于实时打印输出"""
        self._output_callback = callback

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
                timeout=5,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                LoggerManager.info(f"WinDBG 引擎已就绪: {self.windbg_path}")
            else:
                LoggerManager.warning(f"WinDBG 版本检查失败: {result.stderr}")
        except FileNotFoundError:
            LoggerManager.error(f"未找到 WinDBG: {self.windbg_path}")
        except Exception as e:
            LoggerManager.warning(f"WinDBG 可用性检查失败: {str(e)}")

    def _read_output(self):
        """后台线程读取输出"""
        while self._is_running and self._process and self._process.poll() is None:
            try:
                line = self._process.stdout.readline()
                if line:
                    self._output_queue.put(line)
                    # 如果有回调函数，实时调用
                    if self._output_callback:
                        try:
                            self._output_callback(line)
                        except Exception as e:
                            LoggerManager.error(f"输出回调错误: {str(e)}")
            except Exception as e:
                LoggerManager.error(f"读取输出错误: {str(e)}")
                break

    def _start_session(self):
        """启动持久会话"""
        if self._process is not None:
            return

        try:
            # 构建命令
            # -y: 符号路径
            # -z: 加载 dump 文件
            # -lines: 启用行号
            # -c: 初始命令（空字符串只显示提示符）
            cmd = [self.windbg_path, '-y', self.symbol_path, '-lines']
            if self.current_dump:
                cmd.extend(['-z', self.current_dump])

            LoggerManager.debug(f"启动 cdb 会话: {' '.join(cmd)}")

            # 启动进程
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )

            self._is_running = True
            self._output_queue = queue.Queue()

            # 启动输出读取线程
            self._output_thread = threading.Thread(target=self._read_output, daemon=True)
            self._output_thread.start()

            # 等待初始化完成
            self._wait_for_prompt()

            LoggerManager.info("cdb 持久会话已启动")

        except Exception as e:
            self._is_running = False
            if self._process:
                self._process.terminate()
                self._process = None
            raise WinDBGError(f"启动会话失败: {str(e)}")

    def _wait_for_prompt(self, timeout: int = 60):
        """等待提示符出现"""
        output = ""
        start_time = time.time()
        last_output_time = start_time

        LoggerManager.debug(f"开始等待 cdb 提示符，超时时间: {timeout} 秒")

        while time.time() - start_time < timeout:
            try:
                line = self._output_queue.get(timeout=0.1)
                output += line
                last_output_time = time.time()
                
                # 检查各种可能的提示符格式
                if '>' in output:
                    # 检查常见的 cdb 提示符格式
                    if re.search(r'\d+:\d+>', output) or re.search(r'\d+:\s*kd>', output):
                        LoggerManager.debug(f"检测到 cdb 提示符")
                        return True
                
                # 定期输出调试信息
                if len(output) > 0 and len(output) % 500 == 0:
                    LoggerManager.debug(f"已接收 {len(output)} 字符输出")
                    
            except queue.Empty:
                # 如果超过 5 秒没有新输出，可能已经准备好了
                if time.time() - last_output_time > 5 and '>' in output:
                    LoggerManager.debug(f"输出已稳定，检测到提示符")
                    return True
                continue

        # 输出已接收的内容用于调试
        LoggerManager.error(f"等待提示符超时。已接收输出长度: {len(output)}")
        LoggerManager.debug(f"已接收输出内容:\n{output[-1000:] if len(output) > 1000 else output}")
        raise WinDBGError("等待提示符超时")

    def _send_command(self, command: str) -> str:
        """发送命令并获取输出"""
        if not self._process or self._process.poll() is not None:
            raise CommandExecutionError("调试会话未运行")

        try:
            # 清空输出队列
            while not self._output_queue.empty():
                try:
                    self._output_queue.get_nowait()
                except queue.Empty:
                    break

            # 在命令末尾添加标记，用于检测命令完成
            full_command = command + '; .echo DoneDoneDone'

            # 发送命令
            self._process.stdin.write(full_command + '\n')
            self._process.stdin.flush()

            # 收集输出
            output = ""
            start_time = time.time()
            total_timeout = 120  # 总超时时间为 2 分钟

            while time.time() - start_time < total_timeout:
                try:
                    line = self._output_queue.get(timeout=0.1)
                    output += line

                    # 检查是否包含 DoneDoneDone 标记，立即结束
                    if 'DoneDoneDone' in output:
                        marker_pos = output.find('DoneDoneDone')
                        # 移除 DoneDoneDone 标记及其之后的内容
                        if marker_pos > 0:
                            output = output[:marker_pos].rstrip()
                        LoggerManager.debug(f"检测到 DoneDoneDone 标记，命令执行完成，输出长度: {len(output)}")
                        return output
                except queue.Empty:
                    continue

            # 超时处理
            LoggerManager.warning(f"命令执行超时（{total_timeout}秒），未检测到 DoneDoneDone 标记")
            return output

        except Exception as e:
            raise CommandExecutionError(f"发送命令失败: {str(e)}")

    def load_dump(self, dump_path: str) -> bool:
        """加载崩溃转储文件"""
        if not Path(dump_path).exists():
            raise DumpLoadError(f"转储文件不存在: {dump_path}")

        if not dump_path.endswith('.dmp'):
            raise DumpLoadError("文件扩展名必须是 .dmp")

        try:
            # 如果已有会话，先关闭
            if self._process is not None:
                self.close()

            # 设置当前 dump 文件
            self.current_dump = dump_path

            # 启动新会话并加载 dump
            self._start_session()

            LoggerManager.info(f"成功加载转储文件: {dump_path}")
            return True

        except Exception as e:
            self.current_dump = None
            raise DumpLoadError(f"加载转储文件时发生错误: {str(e)}")

    def execute_command(self, command: str) -> CommandResult:
        """执行 WinDBG 命令"""
        if not self.current_dump:
            raise CommandExecutionError("未加载转储文件")

        with self._lock:
            try:
                # 确保会话已启动
                if self._process is None or self._process.poll() is not None:
                    LoggerManager.debug("会话未运行，重新启动")
                    self._start_session()

                LoggerManager.debug(f"执行 WinDBG 命令: {command}")

                # 发送命令并获取输出
                output = self._send_command(command)

                command_result = CommandResult(
                    success=True,
                    output=output,
                    error="",
                    exit_code=0,
                    command=command
                )

                LoggerManager.debug(f"命令执行成功，输出长度: {len(command_result.output)}")

                return command_result

            except Exception as e:
                LoggerManager.error(f"执行命令时发生错误: {str(e)}")
                return CommandResult(
                    success=False,
                    output="",
                    error=str(e),
                    exit_code=-1,
                    command=command
                )

    def get_session_info(self) -> Dict[str, Any]:
        """获取当前会话信息"""
        return {
            "windbg_path": self.windbg_path,
            "symbol_path": self.symbol_path,
            "current_dump": self.current_dump,
            "timeout": self.timeout,
            "is_session_active": self._process is not None and self._process.poll() is None
        }

    def close(self):
        """关闭调试会话"""
        with self._lock:
            self._is_running = False

            if self._process:
                try:
                    # 尝试优雅退出
                    self._process.stdin.write('q\n')
                    self._process.stdin.flush()
                    self._process.wait(timeout=2)
                except:
                    try:
                        self._process.terminate()
                        self._process.wait(timeout=2)
                    except:
                        self._process.kill()

                self._process = None

            if self._output_thread:
                self._output_thread.join(timeout=1)
                self._output_thread = None

            self.current_dump = None
            LoggerManager.info("WinDBG 会话已关闭")

    def is_available(self) -> bool:
        """检查 WinDBG 是否可用"""
        return Path(self.windbg_path).exists()

    def is_dump_loaded(self) -> bool:
        """检查是否已加载转储文件"""
        return self.current_dump is not None and self._process is not None and self._process.poll() is None

    def is_session_active(self) -> bool:
        """检查会话是否活跃"""
        return self._process is not None and self._process.poll() is None

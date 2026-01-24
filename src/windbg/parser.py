"""WinDBG 输出解析器"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from src.output.models import StackFrame, ModuleInfo, ExceptionInfo
from src.core.logger import LoggerManager


class OutputParser:
    """WinDBG 输出解析器"""

    def __init__(self):
        """初始化解析器"""
        self._compile_patterns()

    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 调用栈模式
        self.stack_pattern = re.compile(
            r'([0-9a-fA-F]+)\s+([^\s!]+)!([^\s+]+)\+([0-9a-fx]+)(?:\s+\[([^\]]+)\s+@(\d+)\])?'
        )

        # 模块信息模式
        self.module_pattern = re.compile(
            r'([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([^\s]+)\s+(?:\(([^\)]+)\)\s+)?(.+)'
        )

        # 异常记录模式
        self.exception_pattern = re.compile(
            r'ExceptionCode:\s+([0-9a-fA-F]+)\s+\(([^)]+)\)'
        )

        # 异常地址模式
        self.exception_address_pattern = re.compile(
            r'Faulting Address:\s+([0-9a-fA-F]+)'
        )

    def parse_exception(self, output: str) -> Optional[ExceptionInfo]:
        """解析异常信息"""
        try:
            code_match = self.exception_pattern.search(output)
            address_match = self.exception_address_pattern.search(output)

            if not code_match:
                return None

            code = code_match.group(1)
            description = code_match.group(2)
            address = address_match.group(1) if address_match else "0x00000000"

            return ExceptionInfo(
                code=code,
                description=description,
                address=address
            )
        except Exception as e:
            LoggerManager.warning(f"解析异常信息失败: {str(e)}")
            return None

    def parse_stack_trace(self, output: str) -> List[StackFrame]:
        """解析调用栈"""
        frames = []
        lines = output.split('\n')

        for line in lines:
            match = self.stack_pattern.search(line)
            if match:
                frame = StackFrame(
                    address=match.group(1),
                    module=match.group(2),
                    function=match.group(3),
                    offset=match.group(4),
                    source_file=match.group(5),
                    line_number=int(match.group(6)) if match.group(6) else None
                )
                frames.append(frame)

        LoggerManager.debug(f"解析到 {len(frames)} 个栈帧")
        return frames

    def parse_modules(self, output: str) -> List[ModuleInfo]:
        """解析模块信息"""
        modules = []
        lines = output.split('\n')

        for line in lines:
            match = self.module_pattern.search(line)
            if match:
                module = ModuleInfo(
                    name=match.group(3),
                    base_address=match.group(1),
                    size=match.group(2),
                    path=match.group(4),
                    version=match.group(2) if match.group(2) else None,
                    symbols_loaded=False
                )
                modules.append(module)

        LoggerManager.debug(f"解析到 {len(modules)} 个模块")
        return modules

    def extract_key_info(self, output: str) -> Dict[str, str]:
        """提取关键信息"""
        info = {}

        # 提取异常代码
        exception_match = re.search(r'ExceptionCode:\s+([0-9a-fA-F]+)', output)
        if exception_match:
            info['exception_code'] = exception_match.group(1)

        # 提取异常地址
        address_match = re.search(r'Faulting Address:\s+([0-9a-fA-F]+)', output)
        if address_match:
            info['faulting_address'] = address_match.group(1)

        # 提取进程 ID
        pid_match = re.search(r'Process\s+([0-9]+)', output)
        if pid_match:
            info['process_id'] = pid_match.group(1)

        # 提取线程 ID
        tid_match = re.search(r'Thread\s+([0-9]+)', output)
        if tid_match:
            info['thread_id'] = tid_match.group(1)

        return info

    def clean_output(self, output: str) -> str:
        """清理输出内容"""
        lines = output.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('Microsoft (R) Windows Debugger'):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def extract_error_messages(self, output: str) -> List[str]:
        """提取错误消息"""
        errors = []
        error_patterns = [
            r'ERROR:\s+(.+)',
            r'Failed to',
            r'Unable to',
            r'Cannot',
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            errors.extend(matches)

        return errors

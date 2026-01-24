"""WinDBG 命令执行器"""

from typing import Optional, List

from src.windbg.engine import WinDBGEngine, CommandResult
from src.windbg.commands_map import COMMAND_MAP
from src.windbg.parser import OutputParser
from src.core.logger import LoggerManager
from src.core.exceptions import CommandExecutionError


class CommandExecutor:
    """WinDBG 命令执行器"""

    def __init__(self, engine: WinDBGEngine):
        """初始化命令执行器"""
        self.engine = engine
        self.parser = OutputParser()

    def analyze_crash(self, verbose: bool = True) -> CommandResult:
        """执行崩溃分析 !analyze -v"""
        command = "!analyze -v" if verbose else "!analyze"
        return self.execute(command)

    def get_call_stack(self, verbose: bool = False) -> CommandResult:
        """获取调用栈"""
        command = "kv" if verbose else "k"
        return self.execute(command)

    def get_exception_record(self) -> CommandResult:
        """获取异常记录 .exr -1"""
        return self.execute(".exr -1")

    def get_threads(self, verbose: bool = False) -> CommandResult:
        """获取线程信息"""
        command = "~*" if verbose else "~"
        return self.execute(command)

    def get_modules(self, verbose: bool = False) -> CommandResult:
        """获取模块信息"""
        command = "lmv" if verbose else "lm"
        return self.execute(command)

    def get_memory(self, address: str, size: int = 64) -> CommandResult:
        """查看内存内容"""
        command = f"db {address} L{size}"
        return self.execute(command)

    def get_registers(self) -> CommandResult:
        """查看寄存器"""
        return self.execute("r")

    def disassemble(self, address: Optional[str] = None, count: int = 10) -> CommandResult:
        """反汇编代码"""
        if address:
            command = f"u {address} L{count}"
        else:
            command = f"u L{count}"
        return self.execute(command)

    def reload_symbols(self) -> CommandResult:
        """重新加载符号"""
        return self.execute(".reload")

    def set_symbol_path(self, path: str) -> CommandResult:
        """设置符号路径"""
        command = f".sympath {path}"
        return self.execute(command)

    def get_symbol_path(self) -> CommandResult:
        """获取符号路径"""
        return self.execute(".sympath")

    def execute(self, command: str) -> CommandResult:
        """执行自定义命令"""
        try:
            LoggerManager.info(f"执行命令: {command}")
            result = self.engine.execute_command(command)

            if not result.success:
                LoggerManager.error(f"命令执行失败: {result.error}")
                raise CommandExecutionError(result.error)

            return result

        except Exception as e:
            LoggerManager.error(f"执行命令时发生错误: {str(e)}")
            raise

    def execute_by_alias(self, alias: str, **kwargs) -> CommandResult:
        """通过别名执行命令"""
        if alias not in COMMAND_MAP:
            raise CommandExecutionError(f"未知的命令别名: {alias}")

        command_template = COMMAND_MAP[alias]
        command = command_template.format(**kwargs)
        return self.execute(command)

    def parse_result(self, result: CommandResult) -> dict:
        """解析命令结果"""
        parsed = {
            'raw_output': result.output,
            'exception': self.parser.parse_exception(result.output),
            'stack_trace': self.parser.parse_stack_trace(result.output),
            'modules': self.parser.parse_modules(result.output),
            'key_info': self.parser.extract_key_info(result.output),
            'errors': self.parser.extract_error_messages(result.output)
        }
        return parsed

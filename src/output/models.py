"""分析报告数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class StackFrame:
    """栈帧"""
    address: str
    function: str
    module: str
    offset: str = ""
    source_file: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    base_address: str
    size: str
    path: str
    version: Optional[str] = None
    symbols_loaded: bool = False


@dataclass
class ExceptionInfo:
    """异常信息"""
    code: str
    description: str
    address: str
    flags: str = ""


@dataclass
class AnalysisReport:
    """分析报告"""
    summary: str = ""
    crash_type: str = ""
    exception_code: str = ""
    exception_address: str = ""
    exception_description: str = ""
    call_stack: List[StackFrame] = field(default_factory=list)
    modules: List[ModuleInfo] = field(default_factory=list)
    exception_info: Optional[ExceptionInfo] = None
    root_cause: str = ""
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_output: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    command: str = ""

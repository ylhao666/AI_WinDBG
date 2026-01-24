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

    def to_dict(self) -> dict:
        """转换为可序列化的字典"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, list):
                result[key] = [item.__dict__ if hasattr(item, '__dict__') else item for item in value]
            elif hasattr(value, '__dict__'):
                result[key] = value.__dict__
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'AnalysisReport':
        """从字典创建 AnalysisReport 对象"""
        data = data.copy()
        
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        if 'call_stack' in data and isinstance(data['call_stack'], list):
            data['call_stack'] = [StackFrame(**item) if isinstance(item, dict) else item for item in data['call_stack']]
        
        if 'modules' in data and isinstance(data['modules'], list):
            data['modules'] = [ModuleInfo(**item) if isinstance(item, dict) else item for item in data['modules']]
        
        if 'exception_info' in data and isinstance(data['exception_info'], dict):
            data['exception_info'] = ExceptionInfo(**data['exception_info'])
        elif 'exception_info' in data and data['exception_info'] is None:
            data['exception_info'] = None
        
        return cls(**data)

"""自定义异常类"""


class AIWinDBGError(Exception):
    """AI WinDBG 基础异常"""
    pass


class ConfigError(AIWinDBGError):
    """配置错误"""
    pass


class WinDBGError(AIWinDBGError):
    """WinDBG 基础异常"""
    pass


class DumpLoadError(WinDBGError):
    """转储文件加载失败"""
    pass


class CommandExecutionError(WinDBGError):
    """命令执行失败"""
    pass


class SymbolLoadError(WinDBGError):
    """符号加载失败"""
    pass


class SessionError(WinDBGError):
    """会话错误"""
    pass


class NLPError(AIWinDBGError):
    """自然语言处理错误"""
    pass


class IntentClassificationError(NLPError):
    """意图分类错误"""
    pass


class CommandMappingError(NLPError):
    """命令映射错误"""
    pass


class LLMError(AIWinDBGError):
    """LLM 错误"""
    pass


class APIError(LLMError):
    """API 调用错误"""
    pass


class AnalysisError(LLMError):
    """分析错误"""
    pass


class OutputError(AIWinDBGError):
    """输出处理错误"""
    pass


class FormattingError(OutputError):
    """格式化错误"""
    pass


class ExportError(OutputError):
    """导出错误"""
    pass


class CLIError(AIWinDBGError):
    """CLI 错误"""
    pass


class InputValidationError(CLIError):
    """输入验证错误"""
    pass


class DisplayError(CLIError):
    """显示错误"""
    pass

"""LLM 提示模板"""

from typing import Dict, Any


class PromptTemplates:
    """LLM 提示模板"""

    COMMAND_GENERATION_TEMPLATE = """
你是一个专业的 Windows 调试助手。根据用户的自然语言描述，生成对应的 WinDBG 命令。

用户输入: {user_input}

请分析用户意图并生成 WinDBG 命令。只返回命令，不要解释。

输出格式:
COMMAND: <WinDBG命令>
"""

    INTENT_CLASSIFICATION_TEMPLATE = """
分析以下用户输入，判断其调试意图。

用户输入: {user_input}

可能的意图:
- analyze_crash: 分析崩溃原因
- view_stack: 查看调用栈
- view_exception: 查看异常信息
- view_memory: 查看内存
- view_modules: 查看加载的模块
- view_threads: 查看线程信息
- view_registers: 查看寄存器
- disassemble: 反汇编代码
- load_symbols: 加载符号文件
- custom_command: 自定义 WinDBG 命令
- help: 获取帮助
- exit: 退出程序

请返回最匹配的意图。

输出格式:
INTENT: <意图名称>
CONFIDENCE: <置信度 0-1>
"""

    COMMAND_CONFIRMATION_TEMPLATE = """
用户请求: {user_input}
生成的 WinDBG 命令: {command}

请简要说明这个命令的作用，以便用户确认。

输出格式:
EXPLANATION: <命令说明>
"""

    CRASH_ANALYSIS_TEMPLATE = """
你是一个专业的 Windows 崩溃分析专家。请分析以下 WinDBG 输出，生成结构化的崩溃分析报告。

执行的命令: {command}

WinDBG 输出:
{raw_output}

请提供以下信息:

1. **崩溃摘要** (Summary)
   - 简要描述崩溃情况
   - 崩溃类型和严重程度

2. **异常信息** (Exception Info)
   - 异常代码
   - 异常地址
   - 异常描述

3. **调用栈分析** (Call Stack Analysis)
   - 关键帧分析
   - 崩溃点定位
   - 函数调用链

4. **根因分析** (Root Cause Analysis)
   - 可能的根本原因
   - 问题代码位置
   - 相关模块信息

5. **修复建议** (Fix Suggestions)
   - 具体的修复建议
   - 代码示例（如适用）
   - 预防措施

请以 JSON 格式输出:
{{
  "summary": "...",
  "crash_type": "...",
  "exception_code": "...",
  "exception_address": "...",
  "exception_description": "...",
  "call_stack_analysis": "...",
  "root_cause": "...",
  "suggestions": ["...", "..."],
  "confidence": 0.95
}}
"""

    STACK_ANALYSIS_TEMPLATE = """
分析以下调用栈，识别关键帧和潜在问题。

调用栈:
{stack_trace}

请提供:
1. 关键帧识别
2. 异常传播路径
3. 可能的问题点

输出格式:
{{
  "key_frames": ["...", "..."],
  "exception_path": "...",
  "potential_issues": ["...", "..."]
}}
"""

    MEMORY_ANALYSIS_TEMPLATE = """
分析以下内存转储，识别异常模式。

内存内容:
{memory_dump}

请提供:
1. 内存模式识别
2. 异常数据检测
3. 可能的内存问题

输出格式:
{{
  "patterns": ["...", "..."],
  "anomalies": ["...", "..."],
  "issues": ["...", "..."]
}}
"""

    @classmethod
    def format_command_generation(cls, user_input: str) -> str:
        """格式化命令生成提示"""
        return cls.COMMAND_GENERATION_TEMPLATE.format(user_input=user_input)

    @classmethod
    def format_intent_classification(cls, user_input: str) -> str:
        """格式化意图分类提示"""
        return cls.INTENT_CLASSIFICATION_TEMPLATE.format(user_input=user_input)

    @classmethod
    def format_command_confirmation(cls, user_input: str, command: str) -> str:
        """格式化命令确认提示"""
        return cls.COMMAND_CONFIRMATION_TEMPLATE.format(
            user_input=user_input,
            command=command
        )

    @classmethod
    def format_crash_analysis(cls, command: str, raw_output: str) -> str:
        """格式化崩溃分析提示"""
        return cls.CRASH_ANALYSIS_TEMPLATE.format(
            command=command,
            raw_output=raw_output
        )

    @classmethod
    def format_stack_analysis(cls, stack_trace: str) -> str:
        """格式化调用栈分析提示"""
        return cls.STACK_ANALYSIS_TEMPLATE.format(stack_trace=stack_trace)

    @classmethod
    def format_memory_analysis(cls, memory_dump: str) -> str:
        """格式化内存分析提示"""
        return cls.MEMORY_ANALYSIS_TEMPLATE.format(memory_dump=memory_dump)

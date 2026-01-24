"""意图定义和关键词映射"""

from enum import Enum
from typing import List, Dict


class Intent(Enum):
    """用户意图枚举"""
    ANALYZE_CRASH = "analyze_crash"
    VIEW_STACK = "view_stack"
    VIEW_EXCEPTION = "view_exception"
    VIEW_MEMORY = "view_memory"
    VIEW_MODULES = "view_modules"
    VIEW_THREADS = "view_threads"
    VIEW_REGISTERS = "view_registers"
    DISASSEMBLE = "disassemble"
    LOAD_SYMBOLS = "load_symbols"
    CUSTOM_COMMAND = "custom_command"
    HELP = "help"
    EXIT = "exit"


INTENT_KEYWORDS: Dict[Intent, List[str]] = {
    Intent.ANALYZE_CRASH: [
        "分析", "崩溃", "crash", "analyze", "异常", "exception",
        "问题", "problem", "错误", "error", "故障", "fault"
    ],
    Intent.VIEW_STACK: [
        "调用栈", "堆栈", "stack", "trace", "回溯", "backtrace",
        "函数调用", "function call"
    ],
    Intent.VIEW_EXCEPTION: [
        "异常", "exception", "错误信息", "error info", "异常记录",
        "exception record", "exr"
    ],
    Intent.VIEW_MEMORY: [
        "内存", "memory", "查看内存", "view memory", "dump",
        "地址", "address"
    ],
    Intent.VIEW_MODULES: [
        "模块", "module", "dll", "加载", "loaded", "lm"
    ],
    Intent.VIEW_THREADS: [
        "线程", "thread", "进程", "process", "~"
    ],
    Intent.VIEW_REGISTERS: [
        "寄存器", "register", "r", "寄存器状态", "register state"
    ],
    Intent.DISASSEMBLE: [
        "反汇编", "disassemble", "汇编", "assembly", "u", "代码",
        "code"
    ],
    Intent.LOAD_SYMBOLS: [
        "符号", "symbol", "加载符号", "load symbols", "reload",
        ".reload", ".sympath"
    ],
    Intent.CUSTOM_COMMAND: [
        "!", ".", "执行", "execute", "run", "命令", "command"
    ],
    Intent.HELP: [
        "帮助", "help", "使用", "usage", "说明", "instruction"
    ],
    Intent.EXIT: [
        "退出", "exit", "quit", "结束", "end", "关闭", "close"
    ]
}


INTENT_TO_COMMAND: Dict[Intent, str] = {
    Intent.ANALYZE_CRASH: "!analyze -v",
    Intent.VIEW_STACK: "kv",
    Intent.VIEW_EXCEPTION: ".exr -1",
    Intent.VIEW_MODULES: "lmv",
    Intent.VIEW_THREADS: "~*",
    Intent.VIEW_REGISTERS: "r",
    Intent.DISASSEMBLE: "u",
    Intent.LOAD_SYMBOLS: ".reload /f",
    Intent.CUSTOM_COMMAND: "",
    Intent.HELP: "help",
    Intent.EXIT: "exit"
}

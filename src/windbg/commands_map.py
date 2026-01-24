"""WinDBG 命令映射"""

COMMAND_MAP = {
    "analyze_crash": "!analyze -v",
    "call_stack": "k",
    "call_stack_verbose": "kv",
    "call_stack_detailed": "kp",
    "exception_record": ".exr -1",
    "threads": "~",
    "threads_verbose": "~*",
    "modules": "lm",
    "modules_verbose": "lmv",
    "memory": "d",
    "memory_ascii": "da",
    "memory_unicode": "du",
    "disassemble": "u",
    "registers": "r",
    "reload_symbols": ".reload",
    "set_symbol_path": ".sympath",
    "get_symbol_path": ".sympath",
    "process_info": ".process",
    "thread_info": ".thread",
    "heap": "!heap",
    "handle": "!handle",
}

CRASH_TYPES = {
    "0xC0000005": "Access Violation",
    "0xC0000409": "Stack Buffer Overflow",
    "0xC0000008": "Invalid Handle",
    "0xC000000D": "Invalid Parameter",
    "0xC0000022": "Access Denied",
    "0xC0000006": "In Page I/O Error",
    "0xC000001D": "Illegal Instruction",
    "0xC0000094": "Integer Divide by Zero",
    "0xC00000FD": "Stack Overflow",
    "0xC0000096": "Privileged Instruction",
}

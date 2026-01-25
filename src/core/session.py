"""会话管理器"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path

from src.output.modes import DisplayMode
from src.core.logger import LoggerManager


class SessionState(Enum):
    """会话状态"""
    IDLE = "idle"
    LOADING = "loading"
    READY = "ready"
    ANALYZING = "analyzing"
    ERROR = "error"


class SessionManager:
    """会话管理器"""

    def __init__(self):
        """初始化会话管理器"""
        self.state = SessionState.IDLE
        self.dump_file: Optional[str] = None
        self.display_mode = DisplayMode.SMART
        self.output_history: List[Dict] = []
        self.command_history: List[str] = []
        self.session_start_time = datetime.now()
        self.metadata: Dict = {}
        self.session_active = False
        self.session_pid: Optional[int] = None

    def set_state(self, state: SessionState | str):
        """设置会话状态"""
        if isinstance(state, str):
            try:
                state = SessionState(state.lower())
            except ValueError:
                LoggerManager.warning(f"无效的状态值: {state}，使用默认状态 IDLE")
                state = SessionState.IDLE
        LoggerManager.debug(f"会话状态变更: {self.state.value} -> {state.value}")
        self.state = state

    def get_state(self) -> SessionState:
        """获取会话状态"""
        return self.state

    def load_dump(self, dump_path: str):
        """加载转储文件"""
        if not Path(dump_path).exists():
            raise FileNotFoundError(f"转储文件不存在: {dump_path}")

        self.dump_file = dump_path
        self.set_state(SessionState.LOADING)
        LoggerManager.info(f"加载转储文件: {dump_path}")

    def dump_loaded(self):
        """转储加载完成"""
        self.set_state(SessionState.READY)
        LoggerManager.info("转储文件加载完成")

    def set_session_active(self, active: bool, pid: Optional[int] = None):
        """设置 cdb 会话状态"""
        self.session_active = active
        self.session_pid = pid
        if active:
            LoggerManager.info(f"cdb 会话已激活 (PID: {pid})")
        else:
            LoggerManager.info("cdb 会话已关闭")

    def is_session_active(self) -> bool:
        """检查 cdb 会话是否活跃"""
        return self.session_active

    def get_session_pid(self) -> Optional[int]:
        """获取 cdb 会话 PID"""
        return self.session_pid

    def set_display_mode(self, mode: DisplayMode | str):
        """设置显示模式"""
        if isinstance(mode, str):
            try:
                mode = DisplayMode(mode.lower())
            except ValueError:
                LoggerManager.warning(f"无效的显示模式值: {mode}，使用默认模式 SMART")
                mode = DisplayMode.SMART
        self.display_mode = mode
        LoggerManager.info(f"显示模式设置为: {mode.value}")

    def get_display_mode(self) -> DisplayMode:
        """获取显示模式"""
        return self.display_mode

    def toggle_display_mode(self):
        """切换显示模式"""
        modes = list(DisplayMode)
        current_index = modes.index(self.display_mode)
        next_index = (current_index + 1) % len(modes)
        self.set_display_mode(modes[next_index])

    def add_output(self, output: str, command: str, mode: DisplayMode | str):
        """添加输出到历史"""
        if isinstance(mode, str):
            try:
                mode = DisplayMode(mode.lower())
            except ValueError:
                LoggerManager.warning(f"无效的显示模式值: {mode}，使用默认模式 SMART")
                mode = DisplayMode.SMART
        self.output_history.append({
            "timestamp": datetime.now(),
            "command": command,
            "output": output,
            "mode": mode.value
        })

        # 限制历史记录大小
        if len(self.output_history) > 1000:
            self.output_history = self.output_history[-1000:]

    def get_output_history(self) -> List[Dict]:
        """获取输出历史"""
        return self.output_history

    def add_command(self, command: str):
        """添加命令到历史"""
        self.command_history.append(command)

        # 限制历史记录大小
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]

    def get_command_history(self) -> List[str]:
        """获取命令历史"""
        return self.command_history

    def set_metadata(self, key: str, value: any):
        """设置元数据"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: any = None) -> any:
        """获取元数据"""
        return self.metadata.get(key, default)

    def get_session_info(self) -> Dict:
        """获取会话信息"""
        return {
            "state": self.state.value,
            "dump_file": self.dump_file,
            "display_mode": self.display_mode.value,
            "session_duration": (datetime.now() - self.session_start_time).total_seconds(),
            "output_count": len(self.output_history),
            "command_count": len(self.command_history),
            "metadata": self.metadata,
            "session_active": self.session_active,
            "session_pid": self.session_pid
        }

    def reset(self):
        """重置会话"""
        self.state = SessionState.IDLE
        self.dump_file = None
        self.display_mode = DisplayMode.SMART
        self.output_history = []
        self.command_history = []
        self.session_start_time = datetime.now()
        self.metadata = {}
        self.session_active = False
        self.session_pid = None
        LoggerManager.info("会话已重置")

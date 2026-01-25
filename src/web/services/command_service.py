"""命令服务"""

from typing import Optional, Dict, Any
from src.core.session import SessionManager, SessionState
from src.windbg.engine import WinDBGEngine
from src.windbg.executor import CommandExecutor
from src.nlp.processor import NLPProcessor
from src.core.logger import LoggerManager


class CommandService:
    """命令服务"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        windbg_engine: WinDBGEngine,
        executor: CommandExecutor,
        nlp_processor: NLPProcessor
    ):
        """初始化命令服务"""
        self.session_manager = session_manager
        self.windbg_engine = windbg_engine
        self.executor = executor
        self.nlp_processor = nlp_processor
    
    async def execute(self, command: str, mode: str = "smart") -> Dict[str, Any]:
        """执行 WinDBG 命令"""
        try:
            if not self.windbg_engine.is_dump_loaded():
                raise Exception("请先加载转储文件")
            
            self.session_manager.set_state(SessionState.ANALYZING)
            
            result = self.executor.execute(command)
            
            self.session_manager.add_command(command)
            self.session_manager.add_output(result.output, command, mode)
            
            self.session_manager.set_state(SessionState.READY)
            
            LoggerManager.info(f"命令执行成功: {command}")
            return {
                "success": result.success,
                "output": result.output,
                "command": command,
                "error": result.error if not result.success else None
            }
        
        except Exception as e:
            self.session_manager.set_state(SessionState.ERROR)
            LoggerManager.error(f"命令执行错误: {str(e)}")
            raise
    
    async def execute_natural(self, user_input: str, mode: str = "smart") -> Dict[str, Any]:
        """执行自然语言命令"""
        try:
            if not self.windbg_engine.is_dump_loaded():
                raise Exception("请先加载转储文件")
            
            parsed = self.nlp_processor.parse_input(user_input)
            command = parsed['command']
            confidence = parsed['confidence']
            
            LoggerManager.info(f"自然语言解析: {user_input} -> {command} (置信度: {confidence:.2%})")
            
            self.session_manager.set_state(SessionState.ANALYZING)
            
            result = self.executor.execute(command)
            
            self.session_manager.add_command(user_input)
            self.session_manager.add_output(result.output, user_input, mode)
            
            self.session_manager.set_state(SessionState.READY)
            
            return {
                "success": result.success,
                "output": result.output,
                "command": command,
                "error": result.error if not result.success else None,
                "confidence": confidence
            }
        
        except Exception as e:
            self.session_manager.set_state(SessionState.ERROR)
            LoggerManager.error(f"自然语言处理错误: {str(e)}")
            raise

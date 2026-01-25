"""会话服务"""

from typing import Optional, Dict, Any
from src.core.session import SessionManager, SessionState
from src.windbg.engine import WinDBGEngine
from src.core.logger import LoggerManager


class SessionService:
    """会话服务"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        windbg_engine: WinDBGEngine
    ):
        """初始化会话服务"""
        self.session_manager = session_manager
        self.windbg_engine = windbg_engine
    
    async def load_dump(self, filepath: str) -> Dict[str, Any]:
        """加载转储文件"""
        try:
            if not self.windbg_engine.is_available():
                raise Exception("WinDBG 不可用")
            
            self.session_manager.set_state(SessionState.LOADING)
            success = self.windbg_engine.load_dump(filepath)
            
            if success:
                self.session_manager.load_dump(filepath)
                self.session_manager.dump_loaded()
                
                if self.windbg_engine._process:
                    self.session_manager.set_session_active(True, self.windbg_engine._process.pid)
                
                LoggerManager.info(f"成功加载转储文件: {filepath}")
                return {
                    "success": True,
                    "message": "转储文件加载成功",
                    "dump_file": filepath
                }
            else:
                raise Exception("加载转储文件失败")
        
        except Exception as e:
            LoggerManager.error(f"加载转储文件错误: {str(e)}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """获取会话状态"""
        try:
            session_info = self.windbg_engine.get_session_info()
            
            return {
                "state": self.session_manager.get_state().value,
                "dump_file": self.session_manager.dump_file,
                "display_mode": self.session_manager.get_display_mode().value,
                "session_active": self.session_manager.is_session_active(),
                "session_pid": self.session_manager.get_session_pid(),
                "windbg_available": self.windbg_engine.is_available()
            }
        except Exception as e:
            LoggerManager.error(f"获取会话状态错误: {str(e)}")
            raise
    
    async def close(self) -> Dict[str, Any]:
        """关闭会话"""
        try:
            self.windbg_engine.close()
            self.session_manager.set_session_active(False, None)
            self.session_manager.reset()
            
            LoggerManager.info("会话已关闭")
            return {
                "success": True,
                "message": "会话已关闭"
            }
        except Exception as e:
            LoggerManager.error(f"关闭会话错误: {str(e)}")
            raise
    
    async def get_command_history(self) -> Dict[str, Any]:
        """获取命令历史"""
        try:
            history = self.session_manager.get_command_history()
            return {
                "history": history,
                "count": len(history)
            }
        except Exception as e:
            LoggerManager.error(f"获取命令历史错误: {str(e)}")
            raise

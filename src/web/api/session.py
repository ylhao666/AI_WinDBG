"""会话管理 API"""

import re
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional

from src.core.logger import LoggerManager
from src.core.exceptions import DumpLoadError, WinDBGError
from src.core.session import SessionState


router = APIRouter()


class LoadDumpRequest(BaseModel):
    """加载转储文件请求"""
    filepath: str


class SessionStatusResponse(BaseModel):
    """会话状态响应"""
    state: str
    dump_file: Optional[str]
    display_mode: str
    session_active: bool
    session_pid: Optional[int]
    windbg_available: bool


def validate_file_path(filepath: str) -> tuple[bool, Optional[str]]:
    """
    验证文件路径
    
    Args:
        filepath: 文件路径
        
    Returns:
        (是否有效, 错误信息)
    """
    if not filepath or not isinstance(filepath, str):
        return False, "文件路径无效"
    
    if not filepath.strip():
        return False, "文件路径为空"
    
    if len(filepath) > 260:
        return False, "文件路径过长"
    
    if '..' in filepath:
        return False, "文件路径包含非法字符"
    
    windows_path_pattern = r'^[A-Za-z]:\\(?:[^<>:"|?*\n\r]+\\)*[^<>:"|?*\n\r]*$'
    if not re.match(windows_path_pattern, filepath):
        return False, "文件路径格式不正确"
    
    if not filepath.lower().endswith('.dmp'):
        return False, "文件扩展名必须是 .dmp"
    
    try:
        path = Path(filepath)
        if not path.exists():
            return False, f"文件不存在: {filepath}"
        
        if not path.is_file():
            return False, f"路径不是文件: {filepath}"
        
        file_size = path.stat().st_size
        if file_size == 0:
            return False, "文件为空"
        
        if file_size > 10 * 1024 * 1024 * 1024:
            return False, "文件过大（超过 10GB）"
        
    except Exception as e:
        LoggerManager.error(f"验证文件路径时发生错误: {str(e)}")
        return False, f"验证文件路径时发生错误: {str(e)}"
    
    return True, None


@router.post("/load", response_model=dict)
async def load_dump(
    request: LoadDumpRequest,
    req: Request
):
    """加载转储文件"""
    session_manager = req.app.state.session_manager
    windbg_engine = req.app.state.windbg_engine
    ws_manager = req.app.state.ws_manager
    
    try:
        LoggerManager.info(f"收到加载转储文件请求: {request.filepath}")
        
        is_valid, error_msg = validate_file_path(request.filepath)
        if not is_valid:
            LoggerManager.warning(f"文件路径验证失败: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        LoggerManager.info(f"文件路径验证通过: {request.filepath}")
        
        if not windbg_engine.is_available():
            LoggerManager.error("WinDBG 不可用")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WinDBG 不可用"
            )
        
        session_manager.set_state(SessionState.LOADING)
        LoggerManager.info(f"开始加载转储文件: {request.filepath}")
        
        success = windbg_engine.load_dump(request.filepath)
        
        if success:
            session_manager.load_dump(request.filepath)
            session_manager.dump_loaded()
            
            if windbg_engine._process:
                session_manager.set_session_active(True, windbg_engine._process.pid)
            
            await ws_manager.broadcast_session_update({
                "type": "session_loaded",
                "dump_file": request.filepath,
                "state": "ready"
            })
            
            LoggerManager.info(f"成功加载转储文件: {request.filepath}")
            return {
                "success": True,
                "message": "转储文件加载成功",
                "dump_file": request.filepath
            }
        else:
            session_manager.set_state(SessionState.ERROR)
            LoggerManager.error(f"加载转储文件失败: {request.filepath}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="加载转储文件失败"
            )
    
    except DumpLoadError as e:
        session_manager.set_state(SessionState.ERROR)
        LoggerManager.error(f"加载转储文件错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        session_manager.set_state(SessionState.ERROR)
        LoggerManager.error(f"加载转储文件异常: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"加载转储文件时发生错误: {str(e)}"
        )


@router.get("/status", response_model=SessionStatusResponse)
async def get_session_status(req: Request):
    """获取会话状态"""
    session_manager = req.app.state.session_manager
    windbg_engine = req.app.state.windbg_engine
    
    try:
        session_info = windbg_engine.get_session_info()
        
        state = session_manager.get_state()
        display_mode = session_manager.get_display_mode()
        
        return SessionStatusResponse(
            state=state.value if hasattr(state, 'value') else str(state),
            dump_file=session_manager.dump_file,
            display_mode=display_mode.value if hasattr(display_mode, 'value') else str(display_mode),
            session_active=session_manager.is_session_active(),
            session_pid=session_manager.get_session_pid(),
            windbg_available=windbg_engine.is_available()
        )
    except Exception as e:
        LoggerManager.error(f"获取会话状态错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话状态失败: {str(e)}"
        )


@router.post("/close")
async def close_session(req: Request):
    """关闭会话"""
    session_manager = req.app.state.session_manager
    windbg_engine = req.app.state.windbg_engine
    ws_manager = req.app.state.ws_manager
    
    try:
        LoggerManager.info("收到关闭会话请求")
        windbg_engine.close()
        session_manager.set_session_active(False, None)
        session_manager.reset()
        
        await ws_manager.broadcast_session_update({
            "type": "session_closed",
            "state": "idle"
        })
        
        LoggerManager.info("会话已关闭")
        return {
            "success": True,
            "message": "会话已关闭"
        }
    except Exception as e:
        LoggerManager.error(f"关闭会话错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"关闭会话失败: {str(e)}"
        )


@router.get("/history")
async def get_command_history(req: Request):
    """获取命令历史"""
    session_manager = req.app.state.session_manager
    
    try:
        history = session_manager.get_command_history()
        return {
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        LoggerManager.error(f"获取命令历史错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取命令历史失败: {str(e)}"
        )

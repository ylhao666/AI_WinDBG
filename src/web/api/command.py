"""命令执行 API"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional

from src.core.logger import LoggerManager
from src.core.exceptions import CommandExecutionError
from src.nlp.processor import NLPProcessor
from src.core.session import SessionState


router = APIRouter()


class ExecuteCommandRequest(BaseModel):
    """执行命令请求"""
    command: str
    mode: Optional[str] = "smart"


class ExecuteCommandResponse(BaseModel):
    """执行命令响应"""
    success: bool
    output: str
    command: str
    error: Optional[str] = None


class NaturalLanguageRequest(BaseModel):
    """自然语言请求"""
    input: str
    mode: Optional[str] = "smart"


@router.post("/execute", response_model=ExecuteCommandResponse)
async def execute_command(
    request: ExecuteCommandRequest,
    req: Request
):
    """执行 WinDBG 命令"""
    session_manager = req.app.state.session_manager
    windbg_engine = req.app.state.windbg_engine
    executor = req.app.state.executor
    ws_manager = req.app.state.ws_manager
    
    try:
        # 检查是否已加载转储文件
        if not windbg_engine.is_dump_loaded():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先加载转储文件"
            )
        
        # 设置会话状态
        session_manager.set_state(SessionState.ANALYZING)
        
        # 执行命令
        result = executor.execute(request.command)
        
        # 添加到历史
        session_manager.add_command(request.command)
        session_manager.add_output(result.output, request.command, request.mode)
        
        # 通知 WebSocket 客户端
        await ws_manager.broadcast_output({
            "type": "command_output",
            "command": request.command,
            "output": result.output,
            "success": result.success,
            "mode": request.mode
        })
        
        # 恢复会话状态
        session_manager.set_state(SessionState.READY)
        
        LoggerManager.info(f"命令执行成功: {request.command}")
        return ExecuteCommandResponse(
            success=result.success,
            output=result.output,
            command=request.command,
            error=result.error if not result.success else None
        )
    
    except CommandExecutionError as e:
        session_manager.set_state(SessionState.ERROR)
        LoggerManager.error(f"命令执行错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        session_manager.set_state(SessionState.ERROR)
        LoggerManager.error(f"命令执行异常: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行命令时发生错误: {str(e)}"
        )


@router.post("/natural", response_model=ExecuteCommandResponse)
async def execute_natural_language(
    request: NaturalLanguageRequest,
    req: Request
):
    """执行自然语言命令"""
    session_manager = req.app.state.session_manager
    windbg_engine = req.app.state.windbg_engine
    executor = req.app.state.executor
    nlp_processor = req.app.state.nlp_processor
    ws_manager = req.app.state.ws_manager
    
    try:
        # 检查是否已加载转储文件
        if not windbg_engine.is_dump_loaded():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先加载转储文件"
            )
        
        # 解析自然语言
        parsed = nlp_processor.parse_input(request.input)
        command = parsed['command']
        confidence = parsed['confidence']
        
        LoggerManager.info(f"自然语言解析: {request.input} -> {command} (置信度: {confidence:.2%})")
        
        # 设置会话状态
        session_manager.set_state(SessionState.ANALYZING)
        
        # 执行命令
        result = executor.execute(command)
        
        # 添加到历史
        session_manager.add_command(request.input)
        session_manager.add_output(result.output, request.input, request.mode)
        
        # 通知 WebSocket 客户端
        await ws_manager.broadcast_output({
            "type": "natural_language_output",
            "input": request.input,
            "command": command,
            "output": result.output,
            "success": result.success,
            "confidence": confidence,
            "mode": request.mode
        })
        
        # 恢复会话状态
        session_manager.set_state(SessionState.READY)
        
        return ExecuteCommandResponse(
            success=result.success,
            output=result.output,
            command=command,
            error=result.error if not result.success else None
        )
    
    except Exception as e:
        session_manager.set_state("error")
        LoggerManager.error(f"自然语言处理错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理自然语言时发生错误: {str(e)}"
        )

"""配置管理 API"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.core.logger import LoggerManager


router = APIRouter()


class ConfigResponse(BaseModel):
    """配置响应"""
    app_name: str
    app_version: str
    windbg_path: str
    symbol_path: str
    llm_provider: str
    llm_model: str
    web_enabled: bool
    web_port: int


@router.get("/", response_model=ConfigResponse)
async def get_config(
    config=Depends(lambda r: r.app.state.config),
    windbg_engine=Depends(lambda r: r.app.state.windbg_engine)
):
    """获取配置信息"""
    try:
        return ConfigResponse(
            app_name=config.get_app_name(),
            app_version=config.get_app_version(),
            windbg_path=config.get_windbg_path(),
            symbol_path=config.get_symbol_path(),
            llm_provider=config.get_llm_provider(),
            llm_model=config.get_llm_model(),
            web_enabled=config.is_web_enabled(),
            web_port=config.get_web_port()
        )
    except Exception as e:
        LoggerManager.error(f"获取配置错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取配置失败: {str(e)}"
        )


@router.get("/llm/status")
async def get_llm_status(
    llm_client=Depends(lambda r: r.app.state.llm_client)
):
    """获取 LLM 状态"""
    try:
        return {
            "available": llm_client.is_available(),
            "provider": llm_client.config.get_llm_provider(),
            "model": llm_client.config.get_llm_model()
        }
    except Exception as e:
        LoggerManager.error(f"获取 LLM 状态错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取 LLM 状态失败: {str(e)}"
        )


@router.get("/windbg/status")
async def get_windbg_status(
    windbg_engine=Depends(lambda r: r.app.state.windbg_engine)
):
    """获取 WinDBG 状态"""
    try:
        session_info = windbg_engine.get_session_info()
        return {
            "available": windbg_engine.is_available(),
            "path": windbg_engine.windbg_path,
            "session_active": session_info.get("is_session_active", False),
            "current_dump": session_info.get("current_dump")
        }
    except Exception as e:
        LoggerManager.error(f"获取 WinDBG 状态错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取 WinDBG 状态失败: {str(e)}"
        )

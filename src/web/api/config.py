"""配置管理 API"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
import time

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


class LLMConfigResponse(BaseModel):
    """LLM 配置响应"""
    provider: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    site_url: Optional[str] = None
    site_name: Optional[str] = None
    max_tokens: int
    temperature: float


class LLMConfigUpdateRequest(BaseModel):
    """LLM 配置更新请求"""
    provider: str = Field(..., description="LLM 提供商")
    model: str = Field(..., description="LLM 模型名称")
    api_key: str = Field(..., description="API Key")
    base_url: Optional[str] = Field(None, description="API Base URL")
    site_url: Optional[str] = Field(None, description="Site URL (OpenRouter)")
    site_name: Optional[str] = Field(None, description="Site Name (OpenRouter)")
    max_tokens: Optional[int] = Field(None, description="最大 Token 数")
    temperature: Optional[float] = Field(None, description="温度参数", ge=0, le=1)


@router.get("/", response_model=ConfigResponse)
async def get_config(req: Request):
    """获取配置信息"""
    config = req.app.state.config
    windbg_engine = req.app.state.windbg_engine
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
async def get_llm_status(req: Request):
    """获取 LLM 状态"""
    llm_client = req.app.state.llm_client
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
async def get_windbg_status(req: Request):
    """获取 WinDBG 状态"""
    windbg_engine = req.app.state.windbg_engine
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


@router.get("/llm", response_model=LLMConfigResponse)
async def get_llm_config(req: Request):
    """获取 LLM 配置"""
    config = req.app.state.config
    try:
        return LLMConfigResponse(
            provider=config.get_llm_provider(),
            model=config.get_llm_model(),
            api_key=config.get_llm_api_key(),  # 返回真实的 API Key
            base_url=config.get_llm_base_url(),
            site_url=config.get_llm_site_url(),
            site_name=config.get_llm_site_name(),
            max_tokens=config.get_llm_max_tokens(),
            temperature=config.get_llm_temperature()
        )
    except Exception as e:
        LoggerManager.error(f"获取 LLM 配置错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取 LLM 配置失败: {str(e)}"
        )


@router.put("/llm")
async def update_llm_config(req: Request, request: LLMConfigUpdateRequest):
    """更新 LLM 配置"""
    config = req.app.state.config
    llm_client = req.app.state.llm_client
    try:
        # 更新配置
        config.set("llm.provider", request.provider)
        config.set("llm.model", request.model)
        config.set("llm.api_key", request.api_key)

        if request.base_url is not None:
            config.set("llm.base_url", request.base_url)
        if request.site_url is not None:
            config.set("llm.site_url", request.site_url)
        if request.site_name is not None:
            config.set("llm.site_name", request.site_name)
        if request.max_tokens is not None:
            config.set("llm.max_tokens", request.max_tokens)
        if request.temperature is not None:
            config.set("llm.temperature", request.temperature)

        # 保存配置
        config.save()
        LoggerManager.info("LLM 配置已更新")

        # 重新加载配置
        config._load_config()

        # 重新初始化 LLM 客户端
        llm_client._setup_client()

        return {"message": "配置已保存"}
    except Exception as e:
        LoggerManager.error(f"更新 LLM 配置错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"更新 LLM 配置失败: {str(e)}"
        )


@router.post("/llm/test")
async def test_llm_connection(request: LLMConfigUpdateRequest):
    """测试 LLM 连接"""
    try:
        start_time = time.time()

        # 创建临时客户端
        client_kwargs = {
            "api_key": request.api_key
        }

        if request.base_url:
            client_kwargs["base_url"] = request.base_url

        # 特殊处理 OpenRouter
        if request.provider == "openrouter":
            client_kwargs["base_url"] = request.base_url or "https://openrouter.ai/api/v1"
            client_kwargs["default_headers"] = {}
            if request.site_url:
                client_kwargs["default_headers"]["HTTP-Referer"] = request.site_url
            if request.site_name:
                client_kwargs["default_headers"]["X-Title"] = request.site_name
        elif request.provider == "deepseek":
            client_kwargs["base_url"] = request.base_url or "https://api.deepseek.com"

        client = OpenAI(**client_kwargs)

        # 发送测试请求
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        latency = (time.time() - start_time) * 1000

        return {
            "success": True,
            "message": "连接成功",
            "latency": round(latency, 2)
        }
    except Exception as e:
        LoggerManager.error(f"测试 LLM 连接错误: {str(e)}")
        return {
            "success": False,
            "message": f"连接失败: {str(e)}"
        }

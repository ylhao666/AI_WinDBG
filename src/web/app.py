"""FastAPI 应用主入口"""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.core.config import ConfigManager
from src.core.logger import LoggerManager
from src.core.exceptions import ConfigError
from src.web.api import session, command, analysis, config as config_api
from src.web.websocket.manager import WebSocketManager
from src.web.services.async_analysis_service import AsyncAnalysisService


def create_app(
    config: Optional[ConfigManager] = None,
    session_manager=None,
    windbg_engine=None,
    llm_client=None,
    analyzer=None,
    executor=None,
    nlp_processor=None
) -> FastAPI:
    """创建 FastAPI 应用"""
    
    app_config = config or ConfigManager()
    
    app = FastAPI(
        title=app_config.get_app_name(),
        version=app_config.get_app_version(),
        description="AI WinDBG 崩溃分析器 Web API"
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.get_web_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # WebSocket 管理器
    ws_manager = WebSocketManager()
    
    # 异步分析服务
    async_analysis_service = AsyncAnalysisService(analyzer, ws_manager)
    
    # 依赖注入
    app.state.config = app_config
    app.state.session_manager = session_manager
    app.state.windbg_engine = windbg_engine
    app.state.llm_client = llm_client
    app.state.analyzer = analyzer
    app.state.executor = executor
    app.state.nlp_processor = nlp_processor
    app.state.ws_manager = ws_manager
    app.state.async_analysis_service = async_analysis_service
    
    # 注册路由
    app.include_router(session.router, prefix="/api/session", tags=["session"])
    app.include_router(command.router, prefix="/api/command", tags=["command"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(config_api.router, prefix="/api/config", tags=["config"])
    
    # WebSocket 端点
    @app.websocket("/ws/output")
    async def websocket_output(websocket: WebSocket):
        """实时输出 WebSocket"""
        await ws_manager.connect_output(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await ws_manager.disconnect_output(websocket)
    
    @app.websocket("/ws/session")
    async def websocket_session(websocket: WebSocket):
        """会话状态 WebSocket"""
        await ws_manager.connect_session(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await ws_manager.disconnect_session(websocket)
    
    # 静态文件服务
    static_path = Path(app_config.get_web_static_path())
    if static_path.exists():
        app.mount("/assets", StaticFiles(directory=str(static_path / "assets")), name="assets")
        
        @app.get("/")
        async def root():
            """前端入口"""
            index_file = static_path / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return {"message": "AI WinDBG Web API"}
    else:
        LoggerManager.warning(f"静态文件目录不存在: {static_path}")
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "app_name": app_config.get_app_name(),
            "version": app_config.get_app_version()
        }
    
    # 启动事件
    @app.on_event("startup")
    async def startup_event():
        """启动事件"""
        LoggerManager.info("Web 应用已启动")
    
    # 关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """关闭事件"""
        LoggerManager.info("Web 应用已关闭")
        await ws_manager.disconnect_all()
    
    return app

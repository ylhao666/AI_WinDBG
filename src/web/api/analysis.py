"""智能分析 API"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional

from src.core.logger import LoggerManager
from src.core.exceptions import AnalysisError, LLMError


router = APIRouter()


class AnalyzeRequest(BaseModel):
    """分析请求"""
    raw_output: str
    command: str


class AnalyzeResponse(BaseModel):
    """分析响应"""
    summary: str
    crash_type: str
    exception_code: str
    exception_address: str
    exception_description: str
    root_cause: str
    suggestions: list
    confidence: float


class AnalyzeAsyncRequest(BaseModel):
    """异步分析请求"""
    raw_output: str
    command: str
    use_cache: bool = True
    streaming: bool = False


class AnalyzeAsyncResponse(BaseModel):
    """异步分析响应"""
    task_id: str
    message: str


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    progress: int
    message: str
    result: Optional[dict] = None
    error: Optional[str] = None
    thinking_history: list = []


@router.post("/report", response_model=AnalyzeResponse)
async def get_analysis_report(
    request: AnalyzeRequest,
    req: Request
):
    """获取智能分析报告（同步方式）"""
    analyzer = req.app.state.analyzer
    ws_manager = req.app.state.ws_manager
    
    try:
        # 检查 LLM 是否可用
        if not analyzer.client.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM 不可用"
            )
        
        # 执行分析
        report = analyzer.analyze_output(request.raw_output, request.command)
        
        # 通知 WebSocket 客户端
        await ws_manager.broadcast_output({
            "type": "analysis_report",
            "report": report.to_dict()
        })
        
        LoggerManager.info("智能分析完成")
        return AnalyzeResponse(
            summary=report.summary,
            crash_type=report.crash_type,
            exception_code=report.exception_code,
            exception_address=report.exception_address,
            exception_description=report.exception_description,
            root_cause=report.root_cause,
            suggestions=report.suggestions,
            confidence=report.confidence
        )
    
    except LLMError as e:
        LoggerManager.error(f"LLM 调用错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM 调用失败: {str(e)}"
        )
    except AnalysisError as e:
        LoggerManager.error(f"分析错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能分析失败: {str(e)}"
        )
    except Exception as e:
        LoggerManager.error(f"分析异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析报告时发生错误: {str(e)}"
        )


@router.post("/analyze-async", response_model=AnalyzeAsyncResponse)
async def analyze_async(
    request: AnalyzeAsyncRequest,
    req: Request
):
    """异步分析 WinDBG 输出"""
    async_analysis_service = req.app.state.async_analysis_service
    
    try:
        # 检查 LLM 是否可用
        if not async_analysis_service.analyzer.client.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM 不可用"
            )
        
        # 创建异步分析任务
        if request.streaming:
            task_id = await async_analysis_service.analyze_streaming(
                request.raw_output,
                request.command,
                request.use_cache
            )
        else:
            task_id = await async_analysis_service.analyze_async(
                request.raw_output,
                request.command,
                request.use_cache
            )
        
        LoggerManager.info(f"创建异步分析任务: {task_id}")
        return AnalyzeAsyncResponse(
            task_id=task_id,
            message="分析任务已创建"
        )
    
    except LLMError as e:
        LoggerManager.error(f"LLM 调用错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM 调用失败: {str(e)}"
        )
    except Exception as e:
        LoggerManager.error(f"创建异步分析任务错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建异步分析任务时发生错误: {str(e)}"
        )


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    req: Request
):
    """获取任务状态"""
    async_analysis_service = req.app.state.async_analysis_service
    
    try:
        task_status = await async_analysis_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务不存在: {task_id}"
            )
        
        return TaskStatusResponse(**task_status)
    
    except HTTPException:
        raise
    except Exception as e:
        LoggerManager.error(f"获取任务状态错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务状态时发生错误: {str(e)}"
        )


@router.post("/task/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    req: Request
):
    """取消任务"""
    async_analysis_service = req.app.state.async_analysis_service
    
    try:
        success = await async_analysis_service.cancel_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务不存在或无法取消: {task_id}"
            )
        
        LoggerManager.info(f"取消分析任务: {task_id}")
        return {
            "success": True,
            "message": "任务已取消"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        LoggerManager.error(f"取消任务错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消任务时发生错误: {str(e)}"
        )


@router.post("/clear-cache")
async def clear_analysis_cache(req: Request):
    """清空分析缓存"""
    analyzer = req.app.state.analyzer
    
    try:
        analyzer.clear_cache()
        LoggerManager.info("分析缓存已清空")
        return {
            "success": True,
            "message": "分析缓存已清空"
        }
    except Exception as e:
        LoggerManager.error(f"清空缓存错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空缓存失败: {str(e)}"
        )

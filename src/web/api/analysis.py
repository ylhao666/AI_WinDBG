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


@router.post("/report", response_model=AnalyzeResponse)
async def get_analysis_report(
    request: AnalyzeRequest,
    req: Request
):
    """获取智能分析报告"""
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

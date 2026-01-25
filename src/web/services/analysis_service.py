"""分析服务"""

from typing import Optional, Dict, Any
from src.llm.analyzer import SmartAnalyzer
from src.core.logger import LoggerManager


class AnalysisService:
    """分析服务"""
    
    def __init__(self, analyzer: SmartAnalyzer):
        """初始化分析服务"""
        self.analyzer = analyzer
    
    async def analyze(self, raw_output: str, command: str) -> Dict[str, Any]:
        """分析 WinDBG 输出"""
        try:
            if not self.analyzer.client.is_available():
                raise Exception("LLM 不可用")
            
            report = self.analyzer.analyze_output(raw_output, command)
            
            LoggerManager.info("智能分析完成")
            return {
                "summary": report.summary,
                "crash_type": report.crash_type,
                "exception_code": report.exception_code,
                "exception_address": report.exception_address,
                "exception_description": report.exception_description,
                "root_cause": report.root_cause,
                "suggestions": report.suggestions,
                "confidence": report.confidence
            }
        
        except Exception as e:
            LoggerManager.error(f"分析错误: {str(e)}")
            raise
    
    async def clear_cache(self) -> Dict[str, Any]:
        """清空分析缓存"""
        try:
            self.analyzer.clear_cache()
            LoggerManager.info("分析缓存已清空")
            return {
                "success": True,
                "message": "分析缓存已清空"
            }
        except Exception as e:
            LoggerManager.error(f"清空缓存错误: {str(e)}")
            raise

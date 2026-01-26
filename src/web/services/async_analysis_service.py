"""异步分析服务"""

import asyncio
import uuid
from typing import Optional, Dict, Any, Set
from datetime import datetime

from src.llm.analyzer import SmartAnalyzer
from src.core.logger import LoggerManager
from src.core.exceptions import AnalysisError


class AnalysisTask:
    """分析任务"""
    
    def __init__(self, task_id: str, raw_output: str, command: str):
        """初始化任务"""
        self.task_id = task_id
        self.raw_output = raw_output
        self.command = command
        self.status = "pending"
        self.progress = 0
        self.message = "等待开始..."
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.thinking_history: list = []
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.task: Optional[asyncio.Task] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "thinking_history": self.thinking_history,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class AsyncAnalysisService:
    """异步分析服务"""
    
    def __init__(self, analyzer: SmartAnalyzer, ws_manager=None):
        """初始化异步分析服务"""
        self.analyzer = analyzer
        self.ws_manager = ws_manager
        self.tasks: Dict[str, AnalysisTask] = {}
        self._lock = asyncio.Lock()
    
    async def analyze(
        self,
        raw_output: str,
        command: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """分析 WinDBG 输出（同步方式，用于兼容）"""
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
    
    async def analyze_async(
        self,
        raw_output: str,
        command: str,
        use_cache: bool = True
    ) -> str:
        """异步分析 WinDBG 输出
        
        Args:
            raw_output: WinDBG 原始输出
            command: 执行的命令
            use_cache: 是否使用缓存
            
        Returns:
            任务 ID
        """
        task_id = str(uuid.uuid4())
        task = AnalysisTask(task_id, raw_output, command)
        
        async with self._lock:
            self.tasks[task_id] = task
        
        # 创建后台任务
        task.task = asyncio.create_task(
            self._run_analysis_task(task, use_cache)
        )
        
        LoggerManager.info(f"创建异步分析任务: {task_id}")
        return task_id
    
    async def _run_analysis_task(self, task: AnalysisTask, use_cache: bool):
        """运行分析任务"""
        try:
            task.status = "running"
            task.started_at = datetime.now()
            task.progress = 10
            task.message = "开始分析..."
            
            await self._broadcast_progress(task)
            
            # 进度回调函数
            async def progress_callback(stage: str, message: str, data: Dict[str, Any]):
                task.message = message
                
                if stage == "checking_cache":
                    task.progress = 15
                elif stage == "preparing":
                    task.progress = 20
                elif stage == "analyzing":
                    task.progress = 40
                elif stage == "parsing":
                    task.progress = 80
                elif stage == "completed":
                    task.progress = 100
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = data
                elif stage == "cache_hit":
                    task.progress = 100
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = data
                elif stage == "error":
                    task.status = "error"
                    task.error = data.get("error", "未知错误")
                
                await self._broadcast_progress(task)
            
            # 执行分析
            report = await self.analyzer.analyze_output_async(
                task.raw_output,
                task.command,
                progress_callback,
                use_cache
            )
            
            task.result = report.to_dict()
            task.status = "completed"
            task.completed_at = datetime.now()
            task.progress = 100
            task.message = "分析完成"
            
            await self._broadcast_progress(task)
            
            LoggerManager.info(f"异步分析任务完成: {task.task_id}")
            
        except Exception as e:
            LoggerManager.error(f"异步分析任务失败: {task.task_id}, 错误: {str(e)}")
            task.status = "error"
            task.error = str(e)
            task.message = f"分析失败: {str(e)}"
            task.completed_at = datetime.now()
            
            await self._broadcast_progress(task)
    
    async def analyze_streaming(
        self,
        raw_output: str,
        command: str,
        use_cache: bool = True
    ) -> str:
        """流式分析 WinDBG 输出
        
        Args:
            raw_output: WinDBG 原始输出
            command: 执行的命令
            use_cache: 是否使用缓存
            
        Returns:
            任务 ID
        """
        task_id = str(uuid.uuid4())
        task = AnalysisTask(task_id, raw_output, command)
        
        async with self._lock:
            self.tasks[task_id] = task
        
        # 创建后台任务
        task.task = asyncio.create_task(
            self._run_streaming_analysis_task(task, use_cache)
        )
        
        LoggerManager.info(f"创建流式分析任务: {task_id}")
        return task_id
    
    async def _run_streaming_analysis_task(self, task: AnalysisTask, use_cache: bool):
        """运行流式分析任务"""
        try:
            task.status = "running"
            task.started_at = datetime.now()
            task.progress = 10
            task.message = "开始分析..."
            
            await self._broadcast_progress(task)
            
            # 进度回调函数
            async def progress_callback(stage: str, message: str, data: Dict[str, Any]):
                task.message = message
                
                if stage == "checking_cache":
                    task.progress = 15
                elif stage == "preparing":
                    task.progress = 20
                elif stage == "analyzing":
                    task.progress = 40
                elif stage == "thinking":
                    task.progress = min(task.progress + 1, 90)
                    task.thinking_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "content": data.get("chunk", "")
                    })
                elif stage == "parsing":
                    task.progress = 90
                elif stage == "completed":
                    task.progress = 100
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = data
                elif stage == "cache_hit":
                    task.progress = 100
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = data
                elif stage == "error":
                    task.status = "error"
                    task.error = data.get("error", "未知错误")
                
                await self._broadcast_progress(task)
            
            # 执行流式分析
            async for progress in self.analyzer.analyze_output_streaming(
                task.raw_output,
                task.command,
                progress_callback,
                use_cache
            ):
                if progress["type"] == "completed":
                    task.result = progress["data"]
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.progress = 100
                    task.message = "分析完成"
                elif progress["type"] == "error":
                    task.status = "error"
                    task.error = progress["data"].get("error", "未知错误")
                    task.message = f"分析失败: {task.error}"
                
                await self._broadcast_progress(task)
            
            LoggerManager.info(f"流式分析任务完成: {task.task_id}")
            
        except Exception as e:
            LoggerManager.error(f"流式分析任务失败: {task.task_id}, 错误: {str(e)}")
            task.status = "error"
            task.error = str(e)
            task.message = f"分析失败: {str(e)}"
            task.completed_at = datetime.now()
            
            await self._broadcast_progress(task)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        async with self._lock:
            task = self.tasks.get(task_id)
            if task:
                return task.to_dict()
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        async with self._lock:
            task = self.tasks.get(task_id)
            if task and task.task and not task.task.done():
                task.task.cancel()
                task.status = "cancelled"
                task.message = "任务已取消"
                task.completed_at = datetime.now()
                
                await self._broadcast_progress(task)
                
                LoggerManager.info(f"取消分析任务: {task_id}")
                return True
        return False
    
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
    
    async def _broadcast_progress(self, task: AnalysisTask):
        """广播任务进度"""
        if self.ws_manager:
            await self.ws_manager.broadcast_output({
                "type": "analysis_progress",
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "message": task.message,
                "result": task.result,
                "error": task.error
            })
    

    async def cleanup_old_tasks(self, max_age_seconds: int = 3600):
        """清理旧任务"""
        now = datetime.now()
        async with self._lock:
            to_remove = []
            for task_id, task in self.tasks.items():
                if task.completed_at and (now - task.completed_at).total_seconds() > max_age_seconds:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
            
            if to_remove:
                LoggerManager.info(f"清理了 {len(to_remove)} 个旧任务")
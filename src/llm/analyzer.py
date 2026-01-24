"""智能分析器"""

import json
from typing import Optional, Dict, Any

from src.llm.client import LLMClient
from src.llm.cache import ResponseCache
from src.nlp.templates import PromptTemplates
from src.output.models import AnalysisReport, StackFrame, ExceptionInfo
from src.core.logger import LoggerManager
from src.core.exceptions import AnalysisError


class SmartAnalyzer:
    """智能分析器"""

    def __init__(self, client: Optional[LLMClient] = None, cache_enabled: bool = True):
        """初始化分析器"""
        self.client = client or LLMClient()
        self.cache = ResponseCache() if cache_enabled else None
        self.templates = PromptTemplates()

    def analyze_output(
        self,
        raw_output: str,
        command: str,
        use_cache: bool = True
    ) -> AnalysisReport:
        """分析 WinDBG 输出"""
        if not self.client.is_available():
            raise AnalysisError("LLM 客户端不可用")

        try:
            # 检查缓存
            if use_cache and self.cache:
                cached = self.cache.get(raw_output)
                if cached:
                    LoggerManager.debug("使用缓存的分析结果")
                    return AnalysisReport.from_dict(cached)

            # 生成分析提示
            prompt = self.templates.format_crash_analysis(command, raw_output)

            # 调用 LLM
            response = self.client.generate_json_completion(prompt)

            # 解析响应
            report = self._parse_analysis_response(response)
            report.raw_output = raw_output
            report.command = command

            # 缓存结果
            if use_cache and self.cache:
                self.cache.set(raw_output, report.to_dict())

            LoggerManager.info("智能分析完成")

            return report

        except Exception as e:
            LoggerManager.error(f"分析失败: {str(e)}")
            raise AnalysisError(f"分析失败: {str(e)}")

    def _parse_analysis_response(self, response: Dict[str, Any]) -> AnalysisReport:
        """解析分析响应"""
        try:
            report = AnalysisReport(
                summary=response.get("summary", ""),
                crash_type=response.get("crash_type", ""),
                exception_code=response.get("exception_code", ""),
                exception_address=response.get("exception_address", ""),
                exception_description=response.get("exception_description", ""),
                root_cause=response.get("root_cause", ""),
                suggestions=response.get("suggestions", []),
                confidence=response.get("confidence", 0.0)
            )

            return report

        except Exception as e:
            LoggerManager.error(f"解析分析响应失败: {str(e)}")
            raise AnalysisError(f"解析分析响应失败: {str(e)}")

    def generate_command_from_natural_language(
        self,
        user_input: str,
        use_cache: bool = True
    ) -> str:
        """从自然语言生成命令"""
        if not self.client.is_available():
            raise AnalysisError("LLM 客户端不可用")

        try:
            # 检查缓存
            if use_cache and self.cache:
                cached = self.cache.get(user_input)
                if cached:
                    LoggerManager.debug("使用缓存的命令")
                    return cached

            # 生成提示
            prompt = self.templates.format_command_generation(user_input)

            # 调用 LLM
            response = self.client.generate_completion(prompt)

            # 提取命令
            command = self._extract_command(response)

            # 缓存结果
            if use_cache and self.cache:
                self.cache.set(user_input, command)

            return command

        except Exception as e:
            LoggerManager.error(f"生成命令失败: {str(e)}")
            raise AnalysisError(f"生成命令失败: {str(e)}")

    def _extract_command(self, response: str) -> str:
        """从响应中提取命令"""
        # 查找 COMMAND: 标记
        if "COMMAND:" in response:
            command = response.split("COMMAND:")[1].strip()
            # 移除可能的换行符和多余空格
            command = command.split('\n')[0].strip()
            return command

        # 如果没有标记，返回整个响应
        return response.strip()

    def get_command_explanation(
        self,
        user_input: str,
        command: str,
        use_cache: bool = True
    ) -> str:
        """获取命令说明"""
        if not self.client.is_available():
            raise AnalysisError("LLM 客户端不可用")

        try:
            # 生成提示
            prompt = self.templates.format_command_confirmation(user_input, command)

            # 调用 LLM
            response = self.client.generate_completion(prompt)

            # 提取说明
            explanation = self._extract_explanation(response)

            return explanation

        except Exception as e:
            LoggerManager.error(f"获取命令说明失败: {str(e)}")
            raise AnalysisError(f"获取命令说明失败: {str(e)}")

    def _extract_explanation(self, response: str) -> str:
        """从响应中提取说明"""
        # 查找 EXPLANATION: 标记
        if "EXPLANATION:" in response:
            explanation = response.split("EXPLANATION:")[1].strip()
            return explanation

        # 如果没有标记，返回整个响应
        return response.strip()

    def clear_cache(self):
        """清空缓存"""
        if self.cache:
            self.cache.clear()
            LoggerManager.info("分析器缓存已清空")

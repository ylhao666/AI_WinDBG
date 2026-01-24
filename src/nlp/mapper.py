"""命令映射器"""

from typing import Dict, Optional, Tuple
import re

from src.nlp.intents import Intent, INTENT_TO_COMMAND
from src.nlp.classifier import IntentClassifier
from src.core.logger import LoggerManager
from src.core.exceptions import CommandMappingError


class CommandMapper:
    """命令映射器"""

    def __init__(self):
        """初始化命令映射器"""
        self.classifier = IntentClassifier()
        self._compile_patterns()

    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 内存地址模式
        self.memory_pattern = re.compile(r'(?:内存|memory|地址|address)\s*[:：]?\s*(0x[0-9a-fA-F]+)', re.IGNORECASE)

        # 数量模式
        self.count_pattern = re.compile(r'(?:数量|count|大小|size)\s*[:：]?\s*(\d+)', re.IGNORECASE)

    def map_intent_to_command(self, intent: Intent, params: Optional[Dict] = None) -> str:
        """将意图映射为 WinDBG 命令"""
        params = params or {}

        # 获取基础命令
        command = INTENT_TO_COMMAND.get(intent, "")

        if not command:
            raise CommandMappingError(f"未找到意图对应的命令: {intent.value}")

        # 根据参数调整命令
        if intent == Intent.VIEW_MEMORY and 'address' in params:
            address = params['address']
            count = params.get('count', 64)
            command = f"db {address} L{count}"

        elif intent == Intent.DISASSEMBLE and 'address' in params:
            address = params['address']
            count = params.get('count', 10)
            command = f"u {address} L{count}"

        LoggerManager.debug(f"命令映射: {intent.value} -> {command}")

        return command

    def extract_parameters(self, text: str, intent: Intent) -> Dict:
        """从文本中提取命令参数"""
        params = {}

        # 提取内存地址
        if intent in [Intent.VIEW_MEMORY, Intent.DISASSEMBLE]:
            memory_match = self.memory_pattern.search(text)
            if memory_match:
                params['address'] = memory_match.group(1)

            # 提取数量
            count_match = self.count_pattern.search(text)
            if count_match:
                params['count'] = int(count_match.group(1))

        return params

    def parse_natural_language(self, text: str) -> Tuple[str, float]:
        """解析自然语言输入，返回命令和置信度"""
        try:
            # 分类意图
            intent, confidence = self.classifier.classify(text)

            # 提取参数
            params = self.extract_parameters(text, intent)

            # 映射命令
            command = self.map_intent_to_command(intent, params)

            return command, confidence

        except Exception as e:
            LoggerManager.error(f"解析自然语言失败: {str(e)}")
            raise CommandMappingError(f"解析自然语言失败: {str(e)}")

    def get_command_suggestion(self, partial_input: str) -> list:
        """获取命令建议"""
        suggestions = []

        # 如果是自然语言输入
        if self._is_natural_language(partial_input):
            intent, _ = self.classifier.classify(partial_input)
            command = self.classifier.get_command_for_intent(intent)
            if command:
                suggestions.append(f"自然语言: {command}")

        # 如果是 WinDBG 命令前缀
        elif partial_input.startswith('!') or partial_input.startswith('.'):
            common_commands = [
                "!analyze -v",
                "!heap",
                "!handle",
                ".exr -1",
                ".reload",
                ".sympath"
            ]
            for cmd in common_commands:
                if cmd.startswith(partial_input):
                    suggestions.append(cmd)

        return suggestions

    def _is_natural_language(self, text: str) -> bool:
        """判断是否是自然语言输入"""
        # 简单判断：包含中文或英文单词
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return chinese_chars > 0 or ' ' in text

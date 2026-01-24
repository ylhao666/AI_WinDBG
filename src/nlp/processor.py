"""自然语言处理器"""

from typing import Dict, Optional, Tuple

from src.nlp.classifier import IntentClassifier
from src.nlp.mapper import CommandMapper
from src.nlp.templates import PromptTemplates
from src.nlp.intents import Intent
from src.core.logger import LoggerManager
from src.core.exceptions import NLPError


class NLPProcessor:
    """自然语言处理器"""

    def __init__(self):
        """初始化 NLP 处理器"""
        self.classifier = IntentClassifier()
        self.mapper = CommandMapper()
        self.templates = PromptTemplates()

    def parse_input(self, user_input: str) -> Dict:
        """解析用户输入"""
        if not user_input or not user_input.strip():
            raise NLPError("输入不能为空")

        try:
            # 分类意图
            intent, confidence = self.classifier.classify(user_input)

            # 提取参数
            params = self.mapper.extract_parameters(user_input, intent)

            # 映射命令
            command = self.mapper.map_intent_to_command(intent, params)

            return {
                "intent": intent.value,
                "command": command,
                "confidence": confidence,
                "params": params
            }

        except Exception as e:
            LoggerManager.error(f"解析输入失败: {str(e)}")
            raise NLPError(f"解析输入失败: {str(e)}")

    def classify_intent(self, text: str) -> Tuple[str, float]:
        """分类用户意图"""
        intent, confidence = self.classifier.classify(text)
        return intent.value, confidence

    def extract_parameters(self, text: str, intent: str) -> Dict:
        """提取命令参数"""
        intent_enum = Intent(intent)
        return self.mapper.extract_parameters(text, intent_enum)

    def generate_command(self, intent: str, params: Optional[Dict] = None) -> str:
        """生成 WinDBG 命令"""
        intent_enum = Intent(intent)
        return self.mapper.map_intent_to_command(intent_enum, params)

    def get_command_suggestion(self, partial_input: str) -> list:
        """获取命令建议"""
        return self.mapper.get_command_suggestion(partial_input)

    def is_natural_language(self, text: str) -> bool:
        """判断是否是自然语言输入"""
        return self.mapper._is_natural_language(text)

    def get_prompt_template(self, template_name: str, **kwargs) -> str:
        """获取提示模板"""
        if template_name == "command_generation":
            return self.templates.format_command_generation(kwargs.get("user_input", ""))
        elif template_name == "intent_classification":
            return self.templates.format_intent_classification(kwargs.get("user_input", ""))
        elif template_name == "command_confirmation":
            return self.templates.format_command_confirmation(
                kwargs.get("user_input", ""),
                kwargs.get("command", "")
            )
        elif template_name == "crash_analysis":
            return self.templates.format_crash_analysis(
                kwargs.get("command", ""),
                kwargs.get("raw_output", "")
            )
        else:
            raise NLPError(f"未知的模板名称: {template_name}")

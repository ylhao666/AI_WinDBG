"""意图分类器"""

from typing import Tuple, List
import re

from src.nlp.intents import Intent, INTENT_KEYWORDS
from src.core.logger import LoggerManager
from src.core.exceptions import IntentClassificationError


class IntentClassifier:
    """意图分类器"""

    def __init__(self):
        """初始化意图分类器"""
        self._compile_patterns()

    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 内存地址模式
        self.memory_address_pattern = re.compile(r'0x[0-9a-fA-F]+')

    def classify(self, text: str) -> Tuple[Intent, float]:
        """分类用户意图，返回意图和置信度"""
        if not text or not text.strip():
            raise IntentClassificationError("输入文本为空")

        text = text.lower().strip()

        # 检查是否是自定义命令（以 ! 或 . 开头）
        if text.startswith('!') or text.startswith('.'):
            return Intent.CUSTOM_COMMAND, 1.0

        # 检查是否包含内存地址
        if self.memory_address_pattern.search(text):
            return Intent.VIEW_MEMORY, 0.9

        # 计算每个意图的匹配分数
        scores = {}
        for intent, keywords in INTENT_KEYWORDS.items():
            score = self._calculate_score(text, keywords)
            if score > 0:
                scores[intent] = score

        if not scores:
            return Intent.CUSTOM_COMMAND, 0.3

        # 返回得分最高的意图
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]

        LoggerManager.debug(f"意图分类: {text} -> {best_intent.value} (置信度: {confidence:.2f})")

        return best_intent, confidence

    def _calculate_score(self, text: str, keywords: List[str]) -> float:
        """计算意图匹配分数"""
        score = 0.0
        text_lower = text.lower()

        for keyword in keywords:
            if keyword in text_lower:
                # 完全匹配
                if keyword == text_lower:
                    score += 1.0
                # 部分匹配
                else:
                    score += 0.5

        # 归一化分数
        return min(score / len(keywords), 1.0)

    def get_keywords_for_intent(self, intent: Intent) -> List[str]:
        """获取意图的关键词"""
        return INTENT_KEYWORDS.get(intent, [])

    def get_all_intents(self) -> List[Intent]:
        """获取所有意图"""
        return list(Intent)

    def get_command_for_intent(self, intent: Intent) -> str:
        """获取意图对应的命令"""
        return INTENT_TO_COMMAND.get(intent, "")

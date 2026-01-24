"""LLM 客户端"""

import json
from typing import Optional, Dict, Any
from openai import OpenAI

from src.core.config import ConfigManager
from src.core.logger import LoggerManager
from src.core.exceptions import LLMError, APIError


class LLMClient:
    """LLM 客户端"""

    def __init__(self, config: Optional[ConfigManager] = None):
        """初始化 LLM 客户端"""
        self.config = config or ConfigManager()
        self._setup_client()

    def _setup_client(self):
        """设置客户端"""
        api_key = self.config.get_llm_api_key()

        if not api_key:
            LoggerManager.warning("未配置 LLM API Key，LLM 功能将不可用")
            self.client = None
            return

        try:
            self.client = OpenAI(api_key=api_key)
            LoggerManager.info("LLM 客户端初始化成功")
        except Exception as e:
            LoggerManager.error(f"LLM 客户端初始化失败: {str(e)}")
            self.client = None

    def is_available(self) -> bool:
        """检查 LLM 是否可用"""
        return self.client is not None

    def generate_completion(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """生成补全"""
        if not self.is_available():
            raise LLMError("LLM 客户端不可用")

        try:
            model = self.config.get_llm_model()
            max_tokens = max_tokens or self.config.get_llm_max_tokens()
            temperature = temperature or self.config.get_llm_temperature()

            LoggerManager.debug(f"调用 LLM: {model}, max_tokens={max_tokens}")

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            result = response.choices[0].message.content
            LoggerManager.debug(f"LLM 响应长度: {len(result)}")

            return result

        except Exception as e:
            LoggerManager.error(f"LLM 调用失败: {str(e)}")
            raise APIError(f"LLM 调用失败: {str(e)}")

    def generate_json_completion(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """生成 JSON 格式的补全"""
        try:
            response = self.generate_completion(prompt, max_tokens, temperature)

            # 尝试解析 JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise LLMError("响应中未找到 JSON 数据")

            json_str = response[json_start:json_end]
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            LoggerManager.error(f"JSON 解析失败: {str(e)}")
            raise LLMError(f"JSON 解析失败: {str(e)}")
        except Exception as e:
            LoggerManager.error(f"生成 JSON 补全失败: {str(e)}")
            raise

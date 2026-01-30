"""LLM 客户端"""

import json
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, Callable
from openai import OpenAI, AsyncOpenAI

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
            self.async_client = None
            return

        try:
            # 获取提供商配置
            provider = self.config.get_llm_provider()
            base_url = self.config.get_llm_base_url()
            site_url = self.config.get_llm_site_url()
            site_name = self.config.get_llm_site_name()

            # 构建客户端参数
            client_params = {"api_key": api_key}
            
            # 如果是 OpenRouter，设置 base_url 和自定义头
            if provider == "openrouter":
                if base_url:
                    client_params["base_url"] = base_url
                
                # 设置自定义头用于 OpenRouter 排名
                default_headers = {}
                if site_url:
                    default_headers["HTTP-Referer"] = site_url
                if site_name:
                    default_headers["X-Title"] = site_name
                
                if default_headers:
                    client_params["default_headers"] = default_headers
            
            # 如果是 DeepSeek，设置 base_url
            elif provider == "deepseek":
                # DeepSeek API 使用与 OpenAI 兼容的格式
                # base_url 可以是 https://api.deepseek.com 或 https://api.deepseek.com/v1
                if base_url:
                    client_params["base_url"] = base_url
                else:
                    # 默认使用 DeepSeek 官方 API 地址
                    client_params["base_url"] = "https://api.deepseek.com"

            self.client = OpenAI(**client_params)
            self.async_client = AsyncOpenAI(**client_params)
            LoggerManager.info(f"LLM 客户端初始化成功 (provider: {provider})")
        except Exception as e:
            LoggerManager.error(f"LLM 客户端初始化失败: {str(e)}")
            self.client = None
            self.async_client = None

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
            LoggerManager.debug(f"LLM 响应内容: {result}")
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

    async def generate_streaming_completion(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """生成流式补全
        
        Args:
            prompt: 提示文本
            progress_callback: 进度回调函数，接收 (stage, message, data)
            max_tokens: 最大令牌数
            temperature: 温度参数
            
        Yields:
            生成的文本片段
        """
        if not self.is_available():
            raise LLMError("LLM 客户端不可用")

        try:
            model = self.config.get_llm_model()
            max_tokens = max_tokens or self.config.get_llm_max_tokens()
            temperature = temperature or self.config.get_llm_temperature()

            LoggerManager.debug(f"调用 LLM 流式 API: {model}, max_tokens={max_tokens}")

            if progress_callback:
                await progress_callback("preparing", "准备调用 LLM...", {})

            stream = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            if progress_callback:
                await progress_callback("analyzing", "正在分析...", {})

            full_content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    
                    if progress_callback:
                        await progress_callback("thinking", content, {"chunk": content})
                    
                    yield content

            LoggerManager.debug(f"LLM 流式响应完成，总长度: {len(full_content)}")

        except Exception as e:
            LoggerManager.error(f"LLM 流式调用失败: {str(e)}")
            raise APIError(f"LLM 流式调用失败: {str(e)}")

    async def generate_completion_async(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """异步生成补全
        
        Args:
            prompt: 提示文本
            max_tokens: 最大令牌数
            temperature: 温度参数
            
        Returns:
            生成的完整文本
        """
        if not self.is_available():
            raise LLMError("LLM 客户端不可用")

        try:
            model = self.config.get_llm_model()
            max_tokens = max_tokens or self.config.get_llm_max_tokens()
            temperature = temperature or self.config.get_llm_temperature()

            LoggerManager.debug(f"异步调用 LLM: {model}, max_tokens={max_tokens}")

            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            result = response.choices[0].message.content
            LoggerManager.debug(f"LLM 异步响应内容: {result}")
            LoggerManager.debug(f"LLM 异步响应长度: {len(result)}")

            return result

        except Exception as e:
            LoggerManager.error(f"LLM 异步调用失败: {str(e)}")
            raise APIError(f"LLM 异步调用失败: {str(e)}")

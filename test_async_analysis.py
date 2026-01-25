"""测试异步分析功能"""

import asyncio
from src.llm.client import LLMClient
from src.llm.analyzer import SmartAnalyzer
from src.web.services.async_analysis_service import AsyncAnalysisService
from src.core.config import ConfigManager


async def test_async_analysis():
    """测试异步分析"""
    print("开始测试异步分析功能...")
    
    # 初始化
    config = ConfigManager()
    client = LLMClient(config)
    analyzer = SmartAnalyzer(client, cache_enabled=False)
    
    # 测试流式生成
    if client.is_available():
        print("LLM 客户端可用")
        
        # 测试流式生成
        try:
            async for chunk in client.generate_streaming_completion("你好"):
                print(f"流式生成: {chunk[:20]}...")
                break
        except Exception as e:
            print(f"流式生成失败: {e}")
    else:
        print("LLM 客户端不可用，跳过测试")
    
    print("测试完成!")


if __name__ == "__main__":
    asyncio.run(test_async_analysis())
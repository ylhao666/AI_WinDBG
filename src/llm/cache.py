"""响应缓存"""

import hashlib
import json
import time
from typing import Optional, Any, Dict
from pathlib import Path

from src.core.logger import LoggerManager
from src.core.exceptions import LLMError


class ResponseCache:
    """响应缓存"""

    def __init__(self, cache_dir: str = "~/.ai_windbg_cache", ttl: int = 3600):
        """初始化缓存"""
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.cache: Dict[str, Dict] = {}

        LoggerManager.debug(f"响应缓存初始化: {self.cache_dir}")

    def _get_cache_key(self, prompt: str) -> str:
        """生成缓存键"""
        return hashlib.md5(prompt.encode()).hexdigest()

    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.json"

    def get(self, prompt: str) -> Optional[Any]:
        """获取缓存"""
        key = self._get_cache_key(prompt)

        # 先检查内存缓存
        if key in self.cache:
            cached = self.cache[key]
            if time.time() - cached['timestamp'] < self.ttl:
                LoggerManager.debug("从内存缓存获取响应")
                return cached['data']
            else:
                del self.cache[key]

        # 检查磁盘缓存
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)

                if time.time() - cached['timestamp'] < self.ttl:
                    # 加载到内存缓存
                    self.cache[key] = cached
                    LoggerManager.debug("从磁盘缓存获取响应")
                    return cached['data']
                else:
                    # 过期，删除缓存
                    cache_file.unlink()

            except Exception as e:
                LoggerManager.warning(f"读取缓存失败: {str(e)}")

        return None

    def set(self, prompt: str, data: Any):
        """设置缓存"""
        key = self._get_cache_key(prompt)
        timestamp = time.time()

        # 保存到内存缓存
        self.cache[key] = {
            'data': data,
            'timestamp': timestamp
        }

        # 保存到磁盘缓存
        try:
            cache_file = self._get_cache_file(key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data': data,
                    'timestamp': timestamp
                }, f, ensure_ascii=False, indent=2)

            LoggerManager.debug("响应已缓存")

        except Exception as e:
            LoggerManager.warning(f"保存缓存失败: {str(e)}")

    def clear(self):
        """清空缓存"""
        self.cache = {}

        # 清空磁盘缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                LoggerManager.warning(f"删除缓存文件失败: {str(e)}")

        LoggerManager.info("缓存已清空")

    def cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()

        # 清理内存缓存
        expired_keys = [
            key for key, cached in self.cache.items()
            if current_time - cached['timestamp'] >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

        # 清理磁盘缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)

                if current_time - cached['timestamp'] >= self.ttl:
                    cache_file.unlink()

            except Exception as e:
                LoggerManager.warning(f"清理缓存文件失败: {str(e)}")

        LoggerManager.debug(f"清理了 {len(expired_keys)} 个过期缓存")

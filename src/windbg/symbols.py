"""符号文件管理器"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List

from src.windbg.engine import WinDBGEngine
from src.core.logger import LoggerManager
from src.core.exceptions import SymbolLoadError


class SymbolManager:
    """符号文件管理器"""

    def __init__(self, engine: WinDBGEngine, symbol_path: Optional[str] = None):
        """初始化符号管理器"""
        self.engine = engine
        self.symbol_path = symbol_path or "SRV*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
        self.loaded_modules: List[str] = []

    def set_symbol_path(self, path: str):
        """设置符号路径"""
        self.symbol_path = path
        LoggerManager.info(f"符号路径设置为: {path}")

    def get_symbol_path(self) -> str:
        """获取符号路径"""
        return self.symbol_path

    def load_symbols(self, module: Optional[str] = None) -> bool:
        """加载符号文件"""
        try:
            if module:
                command = f".reload /f {module}"
                LoggerManager.info(f"加载模块符号: {module}")
            else:
                command = ".reload /f"
                LoggerManager.info("加载所有符号")

            result = self.engine.execute_command(command)

            if result.success:
                if module:
                    self.loaded_modules.append(module)
                LoggerManager.info("符号加载成功")
                return True
            else:
                LoggerManager.warning(f"符号加载失败: {result.error}")
                return False

        except Exception as e:
            LoggerManager.error(f"加载符号时发生错误: {str(e)}")
            raise SymbolLoadError(f"加载符号失败: {str(e)}")

    def download_symbols(self, module: str) -> bool:
        """从微软符号服务器下载符号"""
        try:
            LoggerManager.info(f"从符号服务器下载: {module}")
            return self.load_symbols(module)
        except Exception as e:
            LoggerManager.error(f"下载符号失败: {str(e)}")
            return False

    def check_symbol_status(self) -> dict:
        """检查符号状态"""
        try:
            result = self.engine.execute_command("lm")
            lines = result.output.split('\n')

            status = {
                'total_modules': 0,
                'loaded_symbols': 0,
                'missing_symbols': 0,
                'modules': []
            }

            for line in lines:
                if line.strip():
                    status['total_modules'] += 1
                    if '(deferred)' in line:
                        status['missing_symbols'] += 1
                    else:
                        status['loaded_symbols'] += 1
                    status['modules'].append(line.strip())

            return status

        except Exception as e:
            LoggerManager.error(f"检查符号状态失败: {str(e)}")
            return {}

    def create_local_symbol_cache(self, cache_path: str):
        """创建本地符号缓存"""
        try:
            Path(cache_path).mkdir(parents=True, exist_ok=True)
            LoggerManager.info(f"创建符号缓存目录: {cache_path}")
        except Exception as e:
            LoggerManager.error(f"创建符号缓存失败: {str(e)}")
            raise SymbolLoadError(f"创建符号缓存失败: {str(e)}")

    def clear_symbol_cache(self, cache_path: Optional[str] = None):
        """清除符号缓存"""
        try:
            if cache_path and Path(cache_path).exists():
                import shutil
                shutil.rmtree(cache_path)
                LoggerManager.info(f"清除符号缓存: {cache_path}")
        except Exception as e:
            LoggerManager.error(f"清除符号缓存失败: {str(e)}")

    def get_loaded_modules(self) -> List[str]:
        """获取已加载符号的模块列表"""
        return self.loaded_modules.copy()

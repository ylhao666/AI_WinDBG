"""配置管理器"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from src.core.exceptions import ConfigError


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化配置管理器"""
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_env()
        self._load_config()

    def _load_env(self):
        """加载环境变量"""
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)

    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise ConfigError(f"配置文件不存在: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        # 替换环境变量
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_key = value[2:-1]
            return os.getenv(env_key, default)

        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ConfigError(f"保存配置文件失败: {str(e)}")

    def get_app_name(self) -> str:
        """获取应用名称"""
        return self.get("app.name", "AI WinDBG")

    def get_app_version(self) -> str:
        """获取应用版本"""
        return self.get("app.version", "0.1.0")

    def is_debug(self) -> bool:
        """是否调试模式"""
        return self.get("app.debug", False)

    def get_windbg_path(self) -> str:
        """获取 WinDBG 路径"""
        return self.get("windbg.path", "cdb.exe")

    def get_symbol_path(self) -> str:
        """获取符号路径"""
        return self.get("windbg.symbol_path", "SRV*C:\\Symbols*https://msdl.microsoft.com/download/symbols")

    def get_windbg_timeout(self) -> int:
        """获取 WinDBG 超时时间"""
        return self.get("windbg.timeout", 30)

    def get_llm_provider(self) -> str:
        """获取 LLM 提供商"""
        return self.get("llm.provider", "openai")

    def get_llm_model(self) -> str:
        """获取 LLM 模型"""
        return self.get("llm.model", "gpt-4")

    def get_llm_api_key(self) -> str:
        """获取 LLM API Key"""
        api_key = self.get("llm.api_key", "")
        if api_key.startswith("${") and api_key.endswith("}"):
            env_key = api_key[2:-1]
            return os.getenv(env_key, "")
        return api_key

    def get_llm_max_tokens(self) -> int:
        """获取 LLM 最大 token 数"""
        return self.get("llm.max_tokens", 2000)

    def get_llm_temperature(self) -> float:
        """获取 LLM 温度参数"""
        return self.get("llm.temperature", 0.3)

    def get_cli_theme(self) -> str:
        """获取 CLI 主题"""
        return self.get("cli.theme", "dark")

    def get_history_file(self) -> str:
        """获取历史文件路径"""
        return os.path.expanduser(self.get("cli.history_file", "~/.ai_windbg_history"))

    def get_history_size(self) -> int:
        """获取历史记录大小"""
        return self.get("cli.history_size", 100)

    def get_default_display_mode(self) -> str:
        """获取默认显示模式"""
        return self.get("display.default_mode", "smart")

    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get("logging.level", "INFO")

    def get_log_file(self) -> str:
        """获取日志文件路径"""
        return os.path.expanduser(self.get("logging.file", "~/.ai_windbg.log"))

    def is_command_validation_enabled(self) -> bool:
        """是否启用命令验证"""
        return self.get("security.enable_command_validation", True)

    def is_dangerous_commands_allowed(self) -> bool:
        """是否允许危险命令"""
        return self.get("security.allow_dangerous_commands", False)

    def get_max_command_length(self) -> int:
        """获取最大命令长度"""
        return self.get("security.max_command_length", 1000)

"""命令历史记录"""

import os
from typing import List, Optional
from pathlib import Path

from src.core.logger import LoggerManager
from src.core.exceptions import CLIError


class CommandHistory:
    """命令历史记录"""

    def __init__(self, max_size: int = 100, history_file: Optional[str] = None):
        """初始化历史记录"""
        self.history: List[str] = []
        self.index = -1
        self.max_size = max_size
        self.history_file = history_file

        if history_file:
            self.load_from_file()

    def add(self, command: str):
        """添加命令到历史"""
        command = command.strip()
        if not command:
            return

        # 避免重复添加相同的命令
        if self.history and self.history[-1] == command:
            return

        self.history.append(command)

        # 限制历史记录大小
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size:]

        self.index = len(self.history) - 1

        # 保存到文件
        if self.history_file:
            self.save_to_file()

    def get_previous(self) -> Optional[str]:
        """获取上一条命令"""
        if not self.history:
            return None

        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        elif self.index == 0:
            return self.history[0]

        return None

    def get_next(self) -> Optional[str]:
        """获取下一条命令"""
        if not self.history:
            return None

        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]

        return None

    def reset_index(self):
        """重置索引"""
        self.index = len(self.history) - 1

    def search(self, pattern: str) -> List[str]:
        """搜索历史命令"""
        if not pattern:
            return []

        pattern = pattern.lower()
        return [cmd for cmd in self.history if pattern in cmd.lower()]

    def get_all(self) -> List[str]:
        """获取所有历史命令"""
        return self.history.copy()

    def save_to_file(self):
        """保存历史到文件"""
        if not self.history_file:
            return

        try:
            history_path = Path(self.history_file).expanduser()
            history_path.parent.mkdir(parents=True, exist_ok=True)

            with open(history_path, 'w', encoding='utf-8') as f:
                for command in self.history:
                    f.write(command + '\n')

            LoggerManager.debug(f"命令历史已保存到: {history_path}")

        except Exception as e:
            LoggerManager.warning(f"保存命令历史失败: {str(e)}")

    def load_from_file(self):
        """从文件加载历史"""
        if not self.history_file:
            return

        try:
            history_path = Path(self.history_file).expanduser()

            if not history_path.exists():
                return

            with open(history_path, 'r', encoding='utf-8') as f:
                self.history = [line.strip() for line in f if line.strip()]

            self.index = len(self.history) - 1
            LoggerManager.debug(f"从文件加载了 {len(self.history)} 条历史命令")

        except Exception as e:
            LoggerManager.warning(f"加载命令历史失败: {str(e)}")

    def clear(self):
        """清空历史记录"""
        self.history = []
        self.index = -1
        LoggerManager.info("命令历史已清空")

    def get_count(self) -> int:
        """获取历史记录数量"""
        return len(self.history)

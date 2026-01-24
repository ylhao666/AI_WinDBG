"""颜色方案和主题配置"""

from enum import Enum


class ColorScheme:
    """颜色方案"""

    # 基础颜色
    PRIMARY = "bold blue"
    SECONDARY = "cyan"
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"
    INFO = "blue"

    # 语法高亮
    KEYWORD = "bold magenta"
    STRING = "green"
    NUMBER = "yellow"
    COMMENT = "dim white"
    FUNCTION = "cyan"

    # 输出类型
    RAW_OUTPUT = "white"
    SMART_OUTPUT = "blue"
    SYSTEM_MSG = "dim cyan"
    USER_INPUT = "bold green"

    # 边框样式
    BORDER = "dim white"
    HEADER = "bold blue"
    HIGHLIGHT = "yellow"


class DisplayTheme:
    """显示主题配置"""

    DARK = {
        "background": "black",
        "foreground": "white",
        "border": "dim white",
        "header": "bold blue",
        "highlight": "yellow",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }

    LIGHT = {
        "background": "white",
        "foreground": "black",
        "border": "gray",
        "header": "bold blue",
        "highlight": "yellow",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }

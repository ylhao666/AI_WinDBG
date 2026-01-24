"""主应用入口"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.config import ConfigManager
from src.core.logger import LoggerManager
from src.cli.interface import CLIInterface
from src.core.exceptions import ConfigError


def main():
    """主函数"""
    try:
        # 初始化配置
        config = ConfigManager()

        # 初始化日志
        LoggerManager(config)

        LoggerManager.info(f"启动 {config.get_app_name()} v{config.get_app_version()}")

        # 创建并运行 CLI 界面
        cli = CLIInterface(config)
        cli.run()

    except ConfigError as e:
        print(f"配置错误: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        LoggerManager.error("主程序错误", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

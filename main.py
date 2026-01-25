"""主应用入口"""

import sys
import argparse
import asyncio
import threading
from pathlib import Path
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.config import ConfigManager
from src.core.logger import LoggerManager
from src.cli.interface import CLIInterface
from src.core.exceptions import ConfigError
from src.web.app import create_app
from src.windbg.engine import WinDBGEngine
from src.windbg.executor import CommandExecutor
from src.nlp.processor import NLPProcessor
from src.llm.client import LLMClient
from src.llm.analyzer import SmartAnalyzer
from src.core.session import SessionManager
import uvicorn


def initialize_components(config: ConfigManager):
    """初始化共享组件"""
    session = SessionManager()
    windbg = WinDBGEngine(config)
    executor = CommandExecutor(windbg)
    nlp = NLPProcessor()
    llm_client = LLMClient(config)
    analyzer = SmartAnalyzer(llm_client, cache_enabled=True)
    
    return {
        'session_manager': session,
        'windbg_engine': windbg,
        'executor': executor,
        'nlp_processor': nlp,
        'llm_client': llm_client,
        'analyzer': analyzer
    }


def run_cli_mode(config: ConfigManager, components: dict):
    """运行 CLI 模式"""
    try:
        cli = CLIInterface(config)
        cli.run()
    except Exception as e:
        LoggerManager.error(f"CLI 模式错误: {str(e)}", exc_info=True)
        raise


def run_web_mode(config: ConfigManager, components: dict):
    """运行 Web 模式"""
    try:
        app = create_app(
            config=config,
            session_manager=components['session_manager'],
            windbg_engine=components['windbg_engine'],
            llm_client=components['llm_client'],
            analyzer=components['analyzer'],
            executor=components['executor'],
            nlp_processor=components['nlp_processor']
        )
        
        host = config.get_web_host()
        port = config.get_web_port()
        reload = config.is_web_reload_enabled()
        log_level = config.get_web_log_level()
        
        LoggerManager.info(f"启动 Web 服务器: http://{host}:{port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
    except Exception as e:
        LoggerManager.error(f"Web 模式错误: {str(e)}", exc_info=True)
        raise


def run_both_mode(config: ConfigManager, components: dict):
    """运行双模式（CLI + Web）"""
    try:
        app = create_app(
            config=config,
            session_manager=components['session_manager'],
            windbg_engine=components['windbg_engine'],
            llm_client=components['llm_client'],
            analyzer=components['analyzer'],
            executor=components['executor'],
            nlp_processor=components['nlp_processor']
        )
        
        host = config.get_web_host()
        port = config.get_web_port()
        reload = config.is_web_reload_enabled()
        log_level = config.get_web_log_level()
        
        LoggerManager.info(f"启动双模式: CLI + Web (http://{host}:{port})")
        
        # 在单独的线程中启动 Web 服务器
        web_thread = threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={
                'host': host,
                'port': port,
                'reload': reload,
                'log_level': log_level
            },
            daemon=True
        )
        web_thread.start()
        
        # 运行 CLI
        cli = CLIInterface(config)
        cli.run()
        
    except Exception as e:
        LoggerManager.error(f"双模式错误: {str(e)}", exc_info=True)
        raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI WinDBG 崩溃分析器')
    parser.add_argument(
        '--mode',
        choices=['cli', 'web', 'both'],
        default='web',
        help='运行模式: cli (命令行), web (Web界面), both (双模式)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='Web 服务器主机地址'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Web 服务器端口'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化配置
        config = ConfigManager()
        
        # 覆盖命令行参数
        if args.host:
            config.set('web.host', args.host)
        if args.port:
            config.set('web.port', args.port)
        
        # 初始化日志
        LoggerManager(config)
        
        LoggerManager.info(f"启动 {config.get_app_name()} v{config.get_app_version()}")
        LoggerManager.info(f"运行模式: {args.mode}")
        
        # 初始化共享组件
        components = initialize_components(config)
        
        # 根据模式运行
        if args.mode == 'cli':
            run_cli_mode(config, components)
        elif args.mode == 'web':
            run_web_mode(config, components)
        elif args.mode == 'both':
            run_both_mode(config, components)
        
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

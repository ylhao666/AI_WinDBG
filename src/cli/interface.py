"""CLI 界面主控制器"""

import sys
from typing import Optional

from src.core.config import ConfigManager
from src.core.session import SessionManager, SessionState
from src.core.logger import LoggerManager
from src.core.exceptions import CLIError, InputValidationError
from src.windbg.engine import WinDBGEngine
from src.windbg.executor import CommandExecutor
from src.nlp.processor import NLPProcessor
from src.llm.client import LLMClient
from src.llm.analyzer import SmartAnalyzer
from src.cli.display import DisplayManager
from src.cli.history import CommandHistory
from src.cli.validation import InputValidator
from src.cli.themes import DisplayTheme
from src.output.modes import DisplayMode


class CLIInterface:
    """命令行界面主控制器"""

    def __init__(self, config: Optional[ConfigManager] = None):
        """初始化 CLI 界面"""
        self.config = config or ConfigManager()
        self.session = SessionManager()
        self.display = DisplayManager(theme=self.config.get_cli_theme())
        self.validator = InputValidator()

        # 初始化 WinDBG
        self.windbg = WinDBGEngine(self.config)
        self.executor = CommandExecutor(self.windbg)

        # 初始化 NLP 处理器
        self.nlp = NLPProcessor()

        # 初始化 LLM 客户端和分析器
        self.llm_client = LLMClient(self.config)
        self.analyzer = SmartAnalyzer(self.llm_client, cache_enabled=True)

        # 初始化命令历史
        history_file = self.config.get_history_file()
        self.history = CommandHistory(
            max_size=self.config.get_history_size(),
            history_file=history_file
        )

        # 设置默认显示模式
        default_mode = self.config.get_default_display_mode()
        self.session.set_display_mode(DisplayMode(default_mode))

        LoggerManager.info("CLI 界面初始化完成")

    def run(self):
        """运行主循环"""
        try:
            self.display.print_header()
            self.startup_flow()
            self.command_flow()
        except KeyboardInterrupt:
            self.display.print_info("\n用户中断")
        except Exception as e:
            self.display.print_error(f"发生错误: {str(e)}")
            LoggerManager.error(f"运行时错误: {str(e)}", exc_info=True)
        finally:
            self.shutdown()

    def startup_flow(self):
        """启动流程"""
        # 检查 WinDBG 是否可用
        if not self.windbg.is_available():
            self.display.print_warning("未检测到 WinDBG，请安装或配置路径")
            self.display.print_info(f"WinDBG 路径: {self.windbg.windbg_path}")
            return

        self.display.print_success("WinDBG 引擎已就绪")

        # 提示加载转储文件
        self.load_dump_flow()

    def load_dump_flow(self) -> bool:
        """加载转储文件流程"""
        self.display.print_info("请输入转储文件路径（或输入 'exit' 退出）:")

        while True:
            try:
                filepath = input("文件路径> ").strip()

                if filepath.lower() in ['exit', 'quit', 'q']:
                    return False

                if filepath == '':
                    continue

                # 验证文件路径
                valid, msg = self.validator.validate_filepath(filepath)
                if not valid:
                    self.display.print_error(msg)
                    continue

                # 加载转储文件
                self.session.set_state(SessionState.LOADING)
                if self.windbg.load_dump(filepath):
                    self.session.load_dump(filepath)
                    self.session.dump_loaded()
                    self.display.print_success(f"成功加载转储文件: {filepath}")
                    self.display.print_info("输入 'help' 查看可用命令")
                    return True
                else:
                    self.display.print_error("加载转储文件失败")

            except KeyboardInterrupt:
                self.display.print_info("\n取消加载")
                return False
            except Exception as e:
                self.display.print_error(f"加载转储文件时发生错误: {str(e)}")
                LoggerManager.error(f"加载转储文件错误: {str(e)}", exc_info=True)

    def command_flow(self):
        """命令处理流程"""
        while True:
            try:
                user_input = input("> ").strip()

                if not user_input:
                    continue

                # 添加到历史
                self.history.add(user_input)
                self.session.add_command(user_input)

                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break

                if user_input.lower() == 'clear':
                    self.display.clear_screen()
                    continue

                if user_input.lower() == 'help':
                    self.display.print_help()
                    continue

                if user_input.lower().startswith('mode '):
                    self.handle_mode_change(user_input)
                    continue

                if user_input.lower() == 'status':
                    self.show_status()
                    continue

                # 处理普通命令
                self.process_command(user_input)

            except KeyboardInterrupt:
                self.display.print_info("\n按 Ctrl+C 退出")
                break
            except EOFError:
                break
            except Exception as e:
                self.display.print_error(f"发生错误: {str(e)}")
                LoggerManager.error(f"命令处理错误: {str(e)}", exc_info=True)

    def process_command(self, user_input: str):
        """处理用户命令"""
        try:
            # 验证命令
            valid, msg = self.validator.validate_command(user_input)
            if not valid:
                self.display.print_error(msg)
                return

            # 检查是否已加载转储文件
            if not self.windbg.is_dump_loaded():
                self.display.print_warning("请先加载转储文件")
                return

            # 执行命令
            self.session.set_state(SessionState.ANALYZING)

            # 判断是否是自然语言命令
            if self.nlp.is_natural_language(user_input):
                self.process_natural_language(user_input)
                return

            # 执行 WinDBG 命令
            result = self.executor.execute(user_input)

            # 显示结果
            mode = self.session.get_display_mode()
            if mode == DisplayMode.RAW:
                self.display.print_raw_output(result.output)
            elif mode == DisplayMode.SMART:
                self.display.print_raw_output(result.output)
                self.process_smart_analysis(result.output, user_input)
            else:  # BOTH mode
                self.display.print_raw_output(result.output)
                self.process_smart_analysis(result.output, user_input)

            # 添加到输出历史
            self.session.add_output(result.output, user_input, mode)

            self.session.set_state(SessionState.READY)

        except Exception as e:
            self.display.print_error(f"执行命令失败: {str(e)}")
            LoggerManager.error(f"命令执行错误: {str(e)}", exc_info=True)
            self.session.set_state(SessionState.ERROR)

    def process_natural_language(self, user_input: str):
        """处理自然语言输入"""
        try:
            self.display.print_info(f"正在处理: {user_input}")

            # 解析自然语言
            parsed = self.nlp.parse_input(user_input)
            command = parsed['command']
            confidence = parsed['confidence']

            # 显示生成的命令
            self.display.print_info(f"生成的命令: {command} (置信度: {confidence:.2%})")

            # 执行命令
            result = self.executor.execute(command)

            # 显示结果
            mode = self.session.get_display_mode()
            if mode == DisplayMode.RAW:
                self.display.print_raw_output(result.output)
            elif mode == DisplayMode.SMART:
                self.display.print_raw_output(result.output)
                self.process_smart_analysis(result.output, command)
            else:  # BOTH mode
                self.display.print_raw_output(result.output)
                self.process_smart_analysis(result.output, command)

            # 添加到输出历史
            self.session.add_output(result.output, user_input, mode)

            self.session.set_state(SessionState.READY)

        except Exception as e:
            self.display.print_error(f"处理自然语言失败: {str(e)}")
            LoggerManager.error(f"自然语言处理错误: {str(e)}", exc_info=True)
            self.session.set_state(SessionState.ERROR)

    def process_smart_analysis(self, raw_output: str, command: str):
        """处理智能分析"""
        try:
            # 检查 LLM 是否可用
            if not self.llm_client.is_available():
                self.display.print_warning("LLM 不可用，跳过智能分析")
                return

            self.display.print_info("正在进行智能分析...")

            # 执行分析
            report = self.analyzer.analyze_output(raw_output, command)

            # 显示分析报告
            self.display.print_smart_analysis(report)

        except Exception as e:
            self.display.print_warning(f"智能分析失败: {str(e)}")
            LoggerManager.warning(f"智能分析错误: {str(e)}")

    def handle_mode_change(self, command: str):
        """处理模式切换"""
        mode_name = command[5:].strip().lower()

        valid, msg = self.validator.validate_mode(mode_name)
        if not valid:
            self.display.print_error(msg)
            self.display.print_info("可用模式: raw, smart, both")
            return

        self.session.set_display_mode(DisplayMode(mode_name))
        self.display.print_success(f"已切换到 {mode_name} 模式")

    def show_status(self):
        """显示当前状态"""
        status = {
            'mode': self.session.get_display_mode().value,
            'dump_file': self.session.dump_file or '未加载',
            'session_active': self.session.get_state().value
        }
        self.display.print_status(status)

    def shutdown(self):
        """关闭应用"""
        self.display.print_info("正在关闭...")
        self.windbg.close()
        self.history.save_to_file()
        LoggerManager.info("应用已关闭")

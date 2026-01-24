"""显示管理器"""

from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.tree import Tree

from src.output.modes import DisplayMode
from src.output.models import AnalysisReport
from src.cli.themes import ColorScheme
from src.core.logger import LoggerManager
from src.core.exceptions import DisplayError


class DisplayManager:
    """显示管理器"""

    def __init__(self, theme: str = "dark"):
        """初始化显示管理器"""
        self.console = Console()
        self.output_buffer: List[str] = []
        self.max_buffer_size = 1000
        self.theme = theme

    def print_raw_output(self, output: str):
        """打印原始输出"""
        if not output:
            return

        try:
            # 使用语法高亮显示输出
            syntax = Syntax(
                output,
                lexer="asm",
                theme="monokai" if self.theme == "dark" else "default",
                line_numbers=True,
                word_wrap=True
            )
            self.console.print(syntax)
            self._add_to_buffer(output)

        except Exception as e:
            LoggerManager.warning(f"语法高亮失败，使用纯文本显示: {str(e)}")
            self.console.print(output, style=ColorScheme.RAW_OUTPUT)
            self._add_to_buffer(output)

    def print_smart_analysis(self, report: AnalysisReport):
        """打印智能分析报告"""
        if not report:
            return

        try:
            # 创建报告面板
            report_text = self._format_report(report)
            panel = Panel(
                report_text,
                title="[bold blue]崩溃分析报告[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(panel)

        except Exception as e:
            LoggerManager.error(f"显示分析报告失败: {str(e)}")
            raise DisplayError(f"显示分析报告失败: {str(e)}")

    def _format_report(self, report: AnalysisReport) -> str:
        """格式化分析报告"""
        lines = []

        # 摘要
        lines.append(f"\n[bold yellow]📊 崩溃摘要[/bold yellow]")
        lines.append(f"{'─' * 50}")
        lines.append(f"{report.summary}")
        lines.append(f"严重程度: [bold red]Critical[/bold red]" if report.confidence > 0.8 else f"严重程度: [yellow]Medium[/yellow]")
        lines.append(f"置信度: {report.confidence * 100:.1f}%")

        # 异常信息
        if report.exception_info:
            lines.append(f"\n[bold yellow]⚠️  异常信息[/bold yellow]")
            lines.append(f"{'─' * 50}")
            lines.append(f"异常代码: {report.exception_code}")
            lines.append(f"异常地址: {report.exception_address}")
            lines.append(f"异常描述: {report.exception_description}")

        # 调用栈
        if report.call_stack:
            lines.append(f"\n[bold yellow]📍 调用栈[/bold yellow]")
            lines.append(f"{'─' * 50}")
            for i, frame in enumerate(report.call_stack[:10]):
                lines.append(f"{i + 1}. {frame.module}!{frame.function}+{frame.offset}")

        # 根因分析
        if report.root_cause:
            lines.append(f"\n[bold yellow]🔍 根因分析[/bold yellow]")
            lines.append(f"{'─' * 50}")
            lines.append(report.root_cause)

        # 修复建议
        if report.suggestions:
            lines.append(f"\n[bold yellow]💡 修复建议[/bold yellow]")
            lines.append(f"{'─' * 50}")
            for i, suggestion in enumerate(report.suggestions, 1):
                lines.append(f"{i}. {suggestion}")

        return "\n".join(lines)

    def print_info(self, message: str):
        """打印信息"""
        self.console.print(f"[{ColorScheme.INFO}]ℹ️  {message}[/{ColorScheme.INFO}]")

    def print_error(self, message: str):
        """打印错误"""
        self.console.print(f"[{ColorScheme.ERROR}]❌ {message}[/{ColorScheme.ERROR}]")

    def print_warning(self, message: str):
        """打印警告"""
        self.console.print(f"[{ColorScheme.WARNING}]⚠️  {message}[/{ColorScheme.WARNING}]")

    def print_success(self, message: str):
        """打印成功消息"""
        self.console.print(f"[{ColorScheme.SUCCESS}]✅ {message}[/{ColorScheme.SUCCESS}]")

    def print_system(self, message: str):
        """打印系统消息"""
        self.console.print(f"[{ColorScheme.SYSTEM_MSG}]SYSTEM: {message}[/{ColorScheme.SYSTEM_MSG}]")

    def clear_screen(self):
        """清屏"""
        self.console.clear()
        LoggerManager.debug("屏幕已清空")

    def print_header(self):
        """打印应用标题"""
        header = Table.grid(expand=True)
        header.add_column(justify="left")
        header.add_column(justify="right")

        title = f"[{ColorScheme.HEADER}]AI WinDBG 崩溃分析器 v0.1.0[/{ColorScheme.HEADER}]"
        subtitle = f"[dim]Powered by AI & WinDBG[/dim]"

        header.add_row(title, subtitle)
        panel = Panel(header, style="on black")
        self.console.print(panel)

    def print_status(self, status: dict):
        """打印当前状态"""
        table = Table(show_header=False, box=None)
        table.add_column(style="cyan")
        table.add_column(style="white")

        table.add_row("模式:", status.get('mode', 'unknown'))
        table.add_row("转储文件:", status.get('dump_file', '未加载'))
        table.add_row("会话状态:", status.get('session_active', 'inactive'))

        self.console.print(table)

    def print_help(self):
        """打印帮助信息"""
        from rich.align import Align
        from rich.columns import Columns

        help_content = [
            ("[bold yellow]自然语言命令:[/bold yellow]", [
                "  帮我分析崩溃              - 执行崩溃分析",
                "  查看调用栈                - 显示调用栈",
                "  查看异常                  - 显示异常信息",
                "  查看模块                  - 显示加载的模块",
                "  查看线程                  - 显示线程信息"
            ]),
            ("[bold yellow]WinDBG 命令:[/bold yellow]", [
                "  !analyze -v              - 详细崩溃分析",
                "  k / kv                   - 查看调用栈",
                "  .exr -1                  - 查看异常记录",
                "  lm                       - 查看模块列表",
                "  ~                        - 查看线程信息"
            ]),
            ("[bold yellow]系统命令:[/bold yellow]", [
                "  mode <raw|smart|both>    - 切换显示模式",
                "  clear                    - 清屏",
                "  help                     - 显示帮助",
                "  exit / quit              - 退出程序"
            ]),
            ("[bold yellow]快捷键:[/bold yellow]", [
                "  Tab                      - 切换显示模式",
                "  F1                       - 显示帮助",
                "  F2                       - 显示状态",
                "  Ctrl+L                   - 清屏",
                "  Ctrl+C                   - 退出"
            ])
        ]

        for title, commands in help_content:
            self.console.print(title)
            for cmd in commands:
                self.console.print(f"[green]{cmd}[/green]")
            self.console.print()

    def _add_to_buffer(self, output: str):
        """添加输出到缓冲区"""
        self.output_buffer.append(output)

        if len(self.output_buffer) > self.max_buffer_size:
            self.output_buffer = self.output_buffer[-self.max_buffer_size:]

    def get_buffer(self) -> List[str]:
        """获取输出缓冲区"""
        return self.output_buffer.copy()

    def clear_buffer(self):
        """清空缓冲区"""
        self.output_buffer = []

"""
实时监控面板
Agent 6 实现 - 使用 Rich 库创建终端实时 UI
"""

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from dataclasses import dataclass
import time
import threading
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class TradingStats:
    """交易统计"""
    total_balance: float
    daily_profit: float
    total_return_percent: float
    order_count: int
    success_rate: float
    current_strategy: str
    active_positions: int = 0
    recent_trades: List[Dict] = None
    opportunities_found: int = 0
    last_update: str = ""

    def __post_init__(self):
        if self.recent_trades is None:
            self.recent_trades = []
        if not self.last_update:
            self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Dashboard:
    """监控面板类 - 实时终端 UI"""

    def __init__(self, refresh_interval: float = 1.0):
        """
        初始化监控面板

        Args:
            refresh_interval: 刷新间隔（秒），默认 1 秒
        """
        self.console = Console()
        self.refresh_interval = refresh_interval
        self._running = False
        self._live: Optional[Live] = None
        self._thread: Optional[threading.Thread] = None
        self._current_stats: Optional[TradingStats] = None
        self._lock = threading.Lock()

    def update(self, stats: TradingStats) -> None:
        """
        更新显示数据（线程安全）

        Args:
            stats: 最新的交易统计数据
        """
        with self._lock:
            stats.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._current_stats = stats

    def start(self, initial_stats: Optional[TradingStats] = None) -> None:
        """
        启动实时监控

        Args:
            initial_stats: 初始统计数据
        """
        if self._running:
            return

        self._running = True

        # 设置初始数据
        if initial_stats:
            self._current_stats = initial_stats
        else:
            self._current_stats = TradingStats(
                total_balance=0.0,
                daily_profit=0.0,
                total_return_percent=0.0,
                order_count=0,
                success_rate=0.0,
                current_strategy="初始化中..."
            )

        # 启动实时更新线程
        self._thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._live:
            self._live.stop()

    def _refresh_loop(self) -> None:
        """实时刷新循环（在独立线程中运行）"""
        with Live(
            self._generate_layout(),
            console=self.console,
            refresh_per_second=1,
            screen=False
        ) as live:
            self._live = live
            while self._running:
                try:
                    with self._lock:
                        layout = self._generate_layout()
                    live.update(layout)
                    time.sleep(self.refresh_interval)
                except Exception as e:
                    self.console.print(f"[red]监控面板错误: {e}[/red]")
                    time.sleep(1)

    def _generate_layout(self) -> Layout:
        """生成完整的监控布局"""
        layout = Layout()

        # 分割布局：上部（标题和主要统计） + 下部（详细信息）
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # 再分割 body: 左侧（统计）+ 右侧（最近交易）
        layout["body"].split_row(
            Layout(name="stats", ratio=2),
            Layout(name="trades", ratio=1)
        )

        # 设置各部分内容
        layout["header"].update(self._create_header())
        layout["stats"].update(self._create_stats_table())
        layout["trades"].update(self._create_trades_panel())

        return layout

    def _create_header(self) -> Panel:
        """创建标题栏"""
        title = Text("币安套利机器人实时监控", style="bold white on blue")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subtitle = Text(f"最后更新: {timestamp}", style="dim")

        header_text = Text.assemble(title, "\n", subtitle)
        return Panel(header_text, border_style="blue")

    def _create_stats_table(self) -> Table:
        """创建监控表格"""
        with self._lock:
            stats = self._current_stats

        if not stats:
            stats = TradingStats(
                total_balance=0.0,
                daily_profit=0.0,
                total_return_percent=0.0,
                order_count=0,
                success_rate=0.0,
                current_strategy="等待数据..."
            )

        table = Table(title="交易统计", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan", width=20)
        table.add_column("数值", style="yellow", width=30)
        table.add_column("状态", style="green", width=15)

        # 总资金
        balance_status = "✓ 正常" if stats.total_balance > 0 else "⚠ 未知"
        table.add_row(
            "总资金",
            f"{stats.total_balance:.2f} USDT",
            balance_status
        )

        # 今日收益
        profit_color = "green" if stats.daily_profit >= 0 else "red"
        profit_sign = "+" if stats.daily_profit >= 0 else ""
        table.add_row(
            "今日收益",
            f"[{profit_color}]{profit_sign}{stats.daily_profit:.2f} USDT[/{profit_color}]",
            "📈" if stats.daily_profit > 0 else "📉" if stats.daily_profit < 0 else "—"
        )

        # 总收益率
        return_color = "green" if stats.total_return_percent >= 0 else "red"
        return_sign = "+" if stats.total_return_percent >= 0 else ""
        table.add_row(
            "总收益率",
            f"[{return_color}]{return_sign}{stats.total_return_percent:.2f}%[/{return_color}]",
            ""
        )

        # 执行订单数
        table.add_row("执行订单", f"{stats.order_count}", "")

        # 成功率
        success_color = "green" if stats.success_rate >= 80 else "yellow" if stats.success_rate >= 50 else "red"
        table.add_row(
            "成功率",
            f"[{success_color}]{stats.success_rate:.2f}%[/{success_color}]",
            ""
        )

        # 活跃持仓
        table.add_row("活跃持仓", f"{stats.active_positions}", "")

        # 发现机会数
        table.add_row("发现机会", f"{stats.opportunities_found}", "")

        # 当前策略
        table.add_row("当前策略", stats.current_strategy, "🤖 运行中")

        return table

    def _create_trades_panel(self) -> Panel:
        """创建最近交易面板"""
        with self._lock:
            stats = self._current_stats

        if not stats or not stats.recent_trades:
            content = Text("暂无最近交易", style="dim")
            return Panel(content, title="最近交易", border_style="blue")

        # 构建交易列表
        lines = []
        for trade in stats.recent_trades[-5:]:  # 只显示最近 5 笔
            symbol = trade.get("symbol", "UNKNOWN")
            profit = trade.get("profit", 0.0)
            time_str = trade.get("time", "")

            profit_color = "green" if profit >= 0 else "red"
            profit_sign = "+" if profit >= 0 else ""

            line = Text.assemble(
                (f"{time_str}\n", "dim"),
                (f"{symbol}: ", "cyan"),
                (f"{profit_sign}{profit:.2f} USDT\n", profit_color)
            )
            lines.append(line)

        content = Text.assemble(*lines) if lines else Text("无交易", style="dim")
        return Panel(content, title="最近交易", border_style="blue")

    def _create_table(self, stats: TradingStats) -> Table:
        """
        创建简单监控表格（向后兼容）

        Args:
            stats: 交易统计数据

        Returns:
            Rich Table 对象
        """
        table = Table(title="币安套利机器人实时状态")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="magenta")

        table.add_row("总资金", f"{stats.total_balance:.2f} USDT")
        table.add_row("今日收益", f"+{stats.daily_profit:.2f} USDT")
        table.add_row("总收益率", f"{stats.total_return_percent:.2f}%")
        table.add_row("执行订单", f"{stats.order_count}")
        table.add_row("成功率", f"{stats.success_rate:.2f}%")
        table.add_row("当前策略", stats.current_strategy)

        return table

    def print_once(self, stats: TradingStats) -> None:
        """
        打印一次统计信息（非实时模式）

        Args:
            stats: 交易统计数据
        """
        self.console.print(self._create_table(stats))

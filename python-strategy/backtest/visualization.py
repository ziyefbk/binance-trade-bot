"""
数据可视化
Agent 6 实现 - 使用 matplotlib 和 plotly 绘制回测结果
"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List
from pathlib import Path


class BacktestVisualization:
    """回测可视化类"""

    def __init__(self, output_dir: str = "backtest_plots"):
        """
        初始化可视化类

        Args:
            output_dir: 图表输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 设置 matplotlib 中文支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    @staticmethod
    def plot_equity_curve(dates: List[str], equity_values: List[float], show: bool = True) -> None:
        """
        绘制资金曲线

        Args:
            dates: 日期列表
            equity_values: 资金曲线值
            show: 是否显示图表
        """
        fig = go.Figure()

        # 资金曲线
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity_values,
            mode='lines',
            name='资金曲线',
            line=dict(color='#2E86C1', width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 193, 0.2)'
        ))

        # 起始资金线
        if equity_values:
            fig.add_hline(
                y=equity_values[0],
                line_dash="dash",
                line_color="gray",
                annotation_text=f"初始资金: {equity_values[0]:.2f} USDT"
            )

        fig.update_layout(
            title='回测资金曲线',
            xaxis_title='日期',
            yaxis_title='资金 (USDT)',
            hovermode='x unified',
            template='plotly_white'
        )

        # 保存
        output_path = Path("backtest_plots") / "equity_curve.html"
        fig.write_html(str(output_path))
        print(f"✓ 资金曲线已保存: {output_path}")

        if show:
            fig.show()

    @staticmethod
    def plot_drawdown(dates: List[str], drawdown_values: List[float], show: bool = True) -> None:
        """
        绘制回撤曲线

        Args:
            dates: 日期列表
            drawdown_values: 回撤值（百分比）
            show: 是否显示图表
        """
        fig = go.Figure()

        # 回撤曲线（负值表示回撤）
        fig.add_trace(go.Scatter(
            x=dates,
            y=drawdown_values,
            mode='lines',
            name='回撤',
            line=dict(color='#E74C3C', width=2),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.3)'
        ))

        # 最大回撤标注
        if drawdown_values:
            max_dd = min(drawdown_values)
            max_dd_idx = drawdown_values.index(max_dd)
            fig.add_annotation(
                x=dates[max_dd_idx],
                y=max_dd,
                text=f"最大回撤: {max_dd:.2f}%",
                showarrow=True,
                arrowhead=2,
                arrowcolor='red',
                bgcolor='white',
                bordercolor='red'
            )

        fig.update_layout(
            title='回测回撤曲线',
            xaxis_title='日期',
            yaxis_title='回撤 (%)',
            hovermode='x unified',
            template='plotly_white'
        )

        # 保存
        output_path = Path("backtest_plots") / "drawdown.html"
        fig.write_html(str(output_path))
        print(f"✓ 回撤曲线已保存: {output_path}")

        if show:
            fig.show()

    @staticmethod
    def plot_trade_distribution(profits: List[float], show: bool = True) -> None:
        """
        绘制交易盈亏分布

        Args:
            profits: 交易盈亏列表
            show: 是否显示图表
        """
        if not profits:
            print("警告: 没有交易数据可视化")
            return

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('交易盈亏分布', '盈亏饼图'),
            specs=[[{'type': 'histogram'}, {'type': 'pie'}]]
        )

        # 直方图
        fig.add_trace(
            go.Histogram(
                x=profits,
                nbinsx=30,
                name='盈亏分布',
                marker_color='lightblue',
                marker_line_color='darkblue',
                marker_line_width=1
            ),
            row=1, col=1
        )

        # 饼图：盈利 vs 亏损
        winning_trades = len([p for p in profits if p > 0])
        losing_trades = len([p for p in profits if p < 0])
        breakeven_trades = len([p for p in profits if p == 0])

        fig.add_trace(
            go.Pie(
                labels=['盈利', '亏损', '持平'],
                values=[winning_trades, losing_trades, breakeven_trades],
                marker_colors=['#27AE60', '#E74C3C', '#95A5A6']
            ),
            row=1, col=2
        )

        # 统计信息
        total_profit = sum(profits)
        avg_profit = np.mean(profits)
        max_profit = max(profits)
        max_loss = min(profits)

        fig.update_layout(
            title_text=f'交易统计 | 总利润: {total_profit:.2f} USDT | 平均: {avg_profit:.4f} USDT',
            showlegend=True,
            template='plotly_white'
        )

        fig.update_xaxes(title_text="盈亏 (USDT)", row=1, col=1)
        fig.update_yaxes(title_text="交易次数", row=1, col=1)

        # 保存
        output_path = Path("backtest_plots") / "trade_distribution.html"
        fig.write_html(str(output_path))
        print(f"✓ 交易分布已保存: {output_path}")

        if show:
            fig.show()

    @staticmethod
    def plot_all_results(dates: List[str], equity_values: List[float],
                        drawdown_values: List[float], profits: List[float]) -> None:
        """
        绘制所有回测结果（综合图表）

        Args:
            dates: 日期列表
            equity_values: 资金曲线
            drawdown_values: 回撤曲线
            profits: 交易盈亏列表
        """
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('资金曲线', '回撤曲线', '交易盈亏分布'),
            row_heights=[0.4, 0.3, 0.3],
            vertical_spacing=0.1
        )

        # 1. 资金曲线
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=equity_values,
                mode='lines',
                name='资金曲线',
                line=dict(color='#2E86C1', width=2),
                fill='tozeroy'
            ),
            row=1, col=1
        )

        # 2. 回撤曲线
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=drawdown_values,
                mode='lines',
                name='回撤',
                line=dict(color='#E74C3C', width=2),
                fill='tozeroy'
            ),
            row=2, col=1
        )

        # 3. 交易盈亏分布
        if profits:
            fig.add_trace(
                go.Histogram(
                    x=profits,
                    nbinsx=30,
                    name='盈亏分布',
                    marker_color='lightgreen'
                ),
                row=3, col=1
            )

        # 更新布局
        fig.update_xaxes(title_text="日期", row=1, col=1)
        fig.update_yaxes(title_text="资金 (USDT)", row=1, col=1)

        fig.update_xaxes(title_text="日期", row=2, col=1)
        fig.update_yaxes(title_text="回撤 (%)", row=2, col=1)

        fig.update_xaxes(title_text="盈亏 (USDT)", row=3, col=1)
        fig.update_yaxes(title_text="交易次数", row=3, col=1)

        fig.update_layout(
            height=1200,
            title_text="回测综合报告",
            showlegend=True,
            template='plotly_white'
        )

        # 保存
        output_path = Path("backtest_plots") / "comprehensive_report.html"
        fig.write_html(str(output_path))
        print(f"✓ 综合报告已保存: {output_path}")
        fig.show()

    @staticmethod
    def plot_with_matplotlib(dates: List[str], equity_values: List[float],
                            drawdown_values: List[float], profits: List[float]) -> None:
        """
        使用 matplotlib 绘制（用于生成静态图片）

        Args:
            dates: 日期列表
            equity_values: 资金曲线
            drawdown_values: 回撤曲线
            profits: 交易盈亏列表
        """
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle('回测结果报告', fontsize=16, fontweight='bold')

        # 1. 资金曲线
        axes[0].plot(equity_values, color='#2E86C1', linewidth=2)
        axes[0].fill_between(range(len(equity_values)), equity_values, alpha=0.3, color='#2E86C1')
        axes[0].axhline(y=equity_values[0], color='gray', linestyle='--', label='初始资金')
        axes[0].set_title('资金曲线')
        axes[0].set_ylabel('资金 (USDT)')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()

        # 2. 回撤曲线
        axes[1].plot(drawdown_values, color='#E74C3C', linewidth=2)
        axes[1].fill_between(range(len(drawdown_values)), drawdown_values, alpha=0.3, color='#E74C3C')
        axes[1].set_title('回撤曲线')
        axes[1].set_ylabel('回撤 (%)')
        axes[1].grid(True, alpha=0.3)

        # 3. 交易盈亏分布
        if profits:
            axes[2].hist(profits, bins=30, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
            axes[2].axvline(x=0, color='red', linestyle='--', label='盈亏分界线')
            axes[2].set_title('交易盈亏分布')
            axes[2].set_xlabel('盈亏 (USDT)')
            axes[2].set_ylabel('交易次数')
            axes[2].grid(True, alpha=0.3)
            axes[2].legend()

        plt.tight_layout()

        # 保存
        output_path = Path("backtest_plots") / "backtest_report.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✓ 静态图表已保存: {output_path}")
        plt.show()

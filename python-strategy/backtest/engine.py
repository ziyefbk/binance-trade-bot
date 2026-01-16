"""
回测引擎
Agent 6 实现 - 基于历史数据模拟策略执行
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import json


@dataclass
class BacktestResult:
    """回测结果"""
    total_return_percent: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    win_rate: float
    profit_loss_ratio: float
    initial_balance: float = 1000.0
    final_balance: float = 0.0
    equity_curve: List[float] = field(default_factory=list)
    trade_history: List[Dict] = field(default_factory=list)
    dates: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "total_return_percent": self.total_return_percent,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "total_trades": self.total_trades,
            "win_rate": self.win_rate,
            "profit_loss_ratio": self.profit_loss_ratio,
            "initial_balance": self.initial_balance,
            "final_balance": self.final_balance
        }


class BacktestEngine:
    """回测引擎类"""

    def __init__(self, strategy, start_date: str, end_date: str, initial_balance: float = 1000.0):
        """
        初始化回测引擎

        Args:
            strategy: 策略实例
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            initial_balance: 初始资金 (USDT)
        """
        self.strategy = strategy
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.initial_balance = initial_balance
        self.current_balance = initial_balance

        # 回测数据
        self.historical_data: Dict[str, pd.DataFrame] = {}
        self.equity_curve: List[float] = []
        self.trade_history: List[Dict] = []
        self.dates: List[str] = []

        # 回测缓存目录
        self.cache_dir = Path("backtest_data")
        self.cache_dir.mkdir(exist_ok=True)

    def load_historical_data(self, symbols: List[str], interval: str = "1h") -> None:
        """
        加载历史数据

        Args:
            symbols: 交易对列表
            interval: K线间隔 (1m, 5m, 15m, 1h, 4h, 1d)
        """
        print(f"加载历史数据: {self.start_date.date()} 到 {self.end_date.date()}")

        for symbol in symbols:
            cache_file = self.cache_dir / f"{symbol}_{interval}.csv"

            # 尝试从缓存加载
            if cache_file.exists():
                print(f"  从缓存加载 {symbol}...")
                df = pd.read_csv(cache_file, parse_dates=["timestamp"])
            else:
                print(f"  下载 {symbol} 数据...")
                df = self._fetch_binance_klines(symbol, interval)
                # 保存到缓存
                df.to_csv(cache_file, index=False)

            # 过滤日期范围
            df = df[(df["timestamp"] >= self.start_date) & (df["timestamp"] <= self.end_date)]
            self.historical_data[symbol] = df

        print(f"✓ 加载完成，共 {len(symbols)} 个交易对")

    def _fetch_binance_klines(self, symbol: str, interval: str) -> pd.DataFrame:
        """
        从币安获取 K 线数据

        Args:
            symbol: 交易对
            interval: K线间隔

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        # 注意：这里需要真实的币安 API 调用
        # 为了回测，我们生成模拟数据
        print(f"    警告: 使用模拟数据（生产环境请使用真实 API）")

        # 生成日期范围
        date_range = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq=interval.replace("m", "min").replace("h", "H").replace("d", "D")
        )

        # 生成模拟价格数据（随机游走）
        np.random.seed(hash(symbol) % 2**32)  # 使用符号哈希作为种子
        initial_price = 100.0 + np.random.rand() * 900.0
        returns = np.random.randn(len(date_range)) * 0.01  # 1% 波动
        prices = initial_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame({
            "timestamp": date_range,
            "open": prices * (1 + np.random.randn(len(prices)) * 0.001),
            "high": prices * (1 + abs(np.random.randn(len(prices)) * 0.005)),
            "low": prices * (1 - abs(np.random.randn(len(prices)) * 0.005)),
            "close": prices,
            "volume": np.random.rand(len(prices)) * 1000000
        })

        return df

    def run(self) -> BacktestResult:
        """
        运行回测

        Returns:
            BacktestResult 对象
        """
        print("\n开始回测...")
        print(f"初始资金: {self.initial_balance:.2f} USDT")

        # 重置状态
        self.current_balance = self.initial_balance
        self.equity_curve = [self.initial_balance]
        self.trade_history = []
        self.dates = []

        # 获取所有时间戳（使用第一个交易对作为参考）
        first_symbol = list(self.historical_data.keys())[0]
        timestamps = self.historical_data[first_symbol]["timestamp"].tolist()

        # 模拟每个时间点
        for i, timestamp in enumerate(timestamps):
            self.dates.append(timestamp.strftime("%Y-%m-%d %H:%M"))

            # 构建当前市场状态
            current_prices = self._get_prices_at_timestamp(timestamp)

            # 策略决策（简化版，实际需要调用策略的 scan_opportunities）
            opportunities = self._simulate_opportunities(current_prices)

            # 执行交易
            if opportunities:
                for opp in opportunities[:1]:  # 每次只执行最好的机会
                    trade_result = self._execute_trade(opp, timestamp)
                    if trade_result:
                        self.trade_history.append(trade_result)
                        self.current_balance += trade_result["profit"]

            # 记录权益曲线
            self.equity_curve.append(self.current_balance)

            # 进度显示
            if (i + 1) % 100 == 0:
                progress = (i + 1) / len(timestamps) * 100
                print(f"  进度: {progress:.1f}% | 当前资金: {self.current_balance:.2f} USDT")

        # 计算性能指标
        result = self._calculate_metrics()

        print("\n回测完成!")
        print(f"最终资金: {result.final_balance:.2f} USDT")
        print(f"总收益率: {result.total_return_percent:.2f}%")
        print(f"交易次数: {result.total_trades}")
        print(f"胜率: {result.win_rate:.2f}%")

        return result

    def _get_prices_at_timestamp(self, timestamp: datetime) -> Dict[str, float]:
        """获取指定时间的所有交易对价格"""
        prices = {}
        for symbol, df in self.historical_data.items():
            row = df[df["timestamp"] == timestamp]
            if not row.empty:
                prices[symbol] = row.iloc[0]["close"]
        return prices

    def _simulate_opportunities(self, prices: Dict[str, float]) -> List[Dict]:
        """
        模拟发现套利机会（简化版）

        实际应该调用策略的 scan_opportunities 方法
        """
        opportunities = []

        # 简单模拟：随机生成一些机会
        if np.random.rand() < 0.1:  # 10% 概率发现机会
            profit_percent = np.random.rand() * 0.5  # 0-0.5% 利润
            opportunities.append({
                "path": ["BTCUSDT", "ETHBTC", "ETHUSDT"],
                "profit_percent": profit_percent,
                "estimated_amount": min(self.current_balance * 0.1, 100.0)
            })

        return opportunities

    def _execute_trade(self, opportunity: Dict, timestamp: datetime) -> Optional[Dict]:
        """
        执行交易（模拟）

        Returns:
            交易结果字典，如果失败返回 None
        """
        amount = opportunity["estimated_amount"]
        profit_percent = opportunity["profit_percent"]

        # 扣除手续费 (0.1%)
        fee_rate = 0.001
        profit = amount * profit_percent / 100 * (1 - fee_rate * 3)  # 三笔交易

        # 模拟成功率 (90%)
        success = np.random.rand() < 0.9

        if success and profit > 0:
            return {
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
                "path": opportunity["path"],
                "amount": amount,
                "profit": profit,
                "success": True
            }

        return None

    def _calculate_metrics(self) -> BacktestResult:
        """计算回测性能指标"""
        # 总收益率
        total_return = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        # 交易统计
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t["profit"] > 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        # 盈亏比
        winning_profits = [t["profit"] for t in self.trade_history if t["profit"] > 0]
        losing_profits = [abs(t["profit"]) for t in self.trade_history if t["profit"] < 0]
        avg_win = np.mean(winning_profits) if winning_profits else 0.0
        avg_loss = np.mean(losing_profits) if losing_profits else 1.0
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

        # 最大回撤
        max_drawdown = self._calculate_max_drawdown()

        # 夏普比率 (假设无风险利率为 0)
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if len(returns) > 0 and np.std(returns) > 0 else 0.0

        return BacktestResult(
            total_return_percent=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_trades=total_trades,
            win_rate=win_rate,
            profit_loss_ratio=profit_loss_ratio,
            initial_balance=self.initial_balance,
            final_balance=self.current_balance,
            equity_curve=self.equity_curve,
            trade_history=self.trade_history,
            dates=self.dates
        )

    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤百分比"""
        if not self.equity_curve:
            return 0.0

        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max * 100
        return abs(np.min(drawdown))

    def plot_results(self, result: BacktestResult) -> None:
        """
        绘制回测结果

        Args:
            result: 回测结果对象
        """
        from backtest.visualization import BacktestVisualization

        viz = BacktestVisualization()

        # 资金曲线
        viz.plot_equity_curve(result.dates, result.equity_curve)

        # 回撤曲线
        equity_array = np.array(result.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max * 100
        viz.plot_drawdown(result.dates, drawdown.tolist())

        # 交易盈亏分布
        profits = [t["profit"] for t in result.trade_history]
        viz.plot_trade_distribution(profits)

    def save_result(self, result: BacktestResult, filename: str = "backtest_result.json") -> None:
        """
        保存回测结果到文件

        Args:
            result: 回测结果
            filename: 保存文件名
        """
        output_path = self.cache_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"✓ 回测结果已保存到: {output_path}")

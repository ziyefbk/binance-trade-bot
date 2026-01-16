"""
主程序入口
Agent 6 实现 - 完整的主程序逻辑
"""

import argparse
import sys
import signal
import time
from datetime import datetime

# 导入 Rust 引擎（需要先编译 rust-core）
try:
    from binance_rust_py import BinanceEngine
except ImportError:
    print("错误: 无法导入 binance_rust_py 模块")
    print("请先编译 Rust 核心: cd rust-core && maturin develop")
    sys.exit(1)

from config import load_config
from strategies.triangular_arbitrage import TriangularArbitrage
from strategies.hybrid import HybridStrategy
from risk_management.position_manager import PositionManager
from monitor.dashboard import Dashboard, TradingStats
from monitor.logger import TradingLogger
from backtest.engine import BacktestEngine


class TradingBot:
    """交易机器人主类"""

    def __init__(self, config, engine, logger, testnet=False):
        """
        初始化交易机器人

        Args:
            config: 配置对象
            engine: Rust 引擎实例
            logger: 日志记录器
            testnet: 是否使用测试网
        """
        self.config = config
        self.engine = engine
        self.logger = logger
        self.testnet = testnet
        self.running = False

        # 创建组件
        self.position_manager = PositionManager(engine, config.risk)
        self.dashboard = Dashboard(refresh_interval=1.0)
        self.strategy = None

        # 统计数据
        self.start_time = None
        self.initial_balance = 0.0
        self.order_count = 0
        self.successful_orders = 0
        self.opportunities_found = 0
        self.recent_trades = []

    def run(self):
        """运行交易机器人（主循环）"""
        self.running = True
        self.start_time = datetime.now()

        try:
            # 1. 启动市场数据监控
            self.logger.info(f"启动市场数据监控: {len(self.config.trading_pairs)} 个交易对")
            self.engine.start_market_data(self.config.trading_pairs)

            # 2. 获取初始资金
            self.initial_balance = self.position_manager.get_total_balance_usdt()
            self.logger.info(f"初始资金: {self.initial_balance:.2f} USDT")

            # 3. 创建策略
            self.strategy = TriangularArbitrage(self.engine, self.config.triangular)
            self.logger.info("三角套利策略已初始化")

            # 4. 启动监控面板
            initial_stats = self._get_current_stats()
            self.dashboard.start(initial_stats)
            self.logger.info("监控面板已启动")

            # 5. 主循环
            self.logger.info("进入主循环...")
            scan_interval = self.config.triangular.scan_interval_ms / 1000.0

            while self.running:
                try:
                    # 扫描套利机会
                    opportunities = self.strategy.scan_opportunities()
                    self.opportunities_found += len(opportunities)

                    if opportunities:
                        self.logger.info(f"发现 {len(opportunities)} 个套利机会")

                        # 执行最佳机会
                        best_opp = max(opportunities, key=lambda x: x.get("profit_percent", 0))
                        self.logger.info(
                            f"执行套利: {best_opp.get('path')} | "
                            f"预期利润: {best_opp.get('profit_percent', 0):.4f}%"
                        )

                        result = self.strategy.execute(best_opp)
                        self.order_count += 1

                        if result.get("success"):
                            self.successful_orders += 1
                            profit = result.get("profit_usdt", 0)
                            self.logger.info(f"✓ 套利成功，利润: {profit:.4f} USDT")

                            # 记录交易
                            self.recent_trades.append({
                                "symbol": " -> ".join(best_opp.get("path", [])),
                                "profit": profit,
                                "time": datetime.now().strftime("%H:%M:%S")
                            })
                            if len(self.recent_trades) > 10:
                                self.recent_trades = self.recent_trades[-10:]
                        else:
                            error = result.get("error", "未知错误")
                            self.logger.error(f"✗ 套利失败: {error}")

                    # 更新监控面板
                    stats = self._get_current_stats()
                    self.dashboard.update(stats)

                    # 休眠
                    time.sleep(scan_interval)

                except KeyboardInterrupt:
                    self.logger.info("收到停止信号")
                    break
                except Exception as e:
                    self.logger.error(f"主循环错误: {e}", exc_info=True)
                    time.sleep(5)

        finally:
            self.stop()

    def stop(self):
        """停止交易机器人"""
        self.running = False
        self.logger.info("正在停止机器人...")

        # 停止监控面板
        if self.dashboard:
            self.dashboard.stop()

        # 停止市场数据
        try:
            self.engine.stop_market_data()
        except Exception as e:
            self.logger.error(f"停止市场数据失败: {e}")

        # 打印最终统计
        final_stats = self._get_current_stats()
        self.logger.info("=" * 50)
        self.logger.info("最终统计:")
        self.logger.info(f"  运行时间: {self._get_runtime()}")
        self.logger.info(f"  最终资金: {final_stats.total_balance:.2f} USDT")
        self.logger.info(f"  总收益: {final_stats.daily_profit:.2f} USDT ({final_stats.total_return_percent:.2f}%)")
        self.logger.info(f"  执行订单: {final_stats.order_count}")
        self.logger.info(f"  成功率: {final_stats.success_rate:.2f}%")
        self.logger.info("=" * 50)

    def _get_current_stats(self) -> TradingStats:
        """获取当前统计数据"""
        current_balance = self.position_manager.get_total_balance_usdt()
        daily_profit = current_balance - self.initial_balance
        total_return = (daily_profit / self.initial_balance * 100) if self.initial_balance > 0 else 0.0
        success_rate = (self.successful_orders / self.order_count * 100) if self.order_count > 0 else 0.0

        return TradingStats(
            total_balance=current_balance,
            daily_profit=daily_profit,
            total_return_percent=total_return,
            order_count=self.order_count,
            success_rate=success_rate,
            current_strategy="三角套利",
            active_positions=len(self.position_manager.get_all_positions()),
            recent_trades=self.recent_trades.copy(),
            opportunities_found=self.opportunities_found
        )

    def _get_runtime(self) -> str:
        """获取运行时长"""
        if not self.start_time:
            return "0秒"
        delta = datetime.now() - self.start_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        return f"{hours}小时{minutes}分{seconds}秒"


def run_backtest(config, logger):
    """
    运行回测模式

    Args:
        config: 配置对象
        logger: 日志记录器
    """
    logger.info("=" * 50)
    logger.info("回测模式")
    logger.info("=" * 50)

    # 创建 Mock 引擎用于回测
    from unittest.mock import Mock
    mock_engine = Mock()

    # 创建策略
    strategy = TriangularArbitrage(mock_engine, config.triangular)

    # 创建回测引擎
    backtest = BacktestEngine(
        strategy=strategy,
        start_date="2024-01-01",
        end_date="2024-01-31",
        initial_balance=1000.0
    )

    # 加载历史数据
    symbols = config.trading_pairs[:6]  # 使用前 6 个交易对
    backtest.load_historical_data(symbols, interval="1h")

    # 运行回测
    result = backtest.run()

    # 显示结果
    logger.info("\n" + "=" * 50)
    logger.info("回测结果:")
    logger.info("=" * 50)
    logger.info(f"总收益率: {result.total_return_percent:.2f}%")
    logger.info(f"夏普比率: {result.sharpe_ratio:.2f}")
    logger.info(f"最大回撤: {result.max_drawdown:.2f}%")
    logger.info(f"总交易次数: {result.total_trades}")
    logger.info(f"胜率: {result.win_rate:.2f}%")
    logger.info(f"盈亏比: {result.profit_loss_ratio:.2f}")
    logger.info("=" * 50)

    # 保存结果
    backtest.save_result(result)

    # 绘制图表
    try:
        logger.info("\n正在生成可视化图表...")
        backtest.plot_results(result)
        logger.info("✓ 图表生成完成，请在 backtest_plots/ 目录查看")
    except Exception as e:
        logger.error(f"生成图表失败: {e}")


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="币安套利机器人",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --testnet                  # 测试网模式
  python main.py --config my_config.yaml    # 指定配置文件
  python main.py --backtest                 # 回测模式
        """
    )
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--testnet", action="store_true", help="使用测试网")
    parser.add_argument("--backtest", action="store_true", help="运行回测模式")
    args = parser.parse_args()

    # 初始化日志
    logger = TradingLogger()
    logger.info("=" * 50)
    logger.info("币安套利机器人启动")
    logger.info(f"版本: 1.0.0 | 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    try:
        # 加载配置
        logger.info(f"加载配置: {args.config}")
        config = load_config(args.config)
        logger.info("✓ 配置加载成功")

        if args.backtest:
            # 回测模式
            run_backtest(config, logger)
        else:
            # 实盘模式
            logger.info("进入实盘模式")

            # 创建 Rust 引擎
            engine = BinanceEngine(
                api_key=config.api.key,
                api_secret=config.api.secret,
                testnet=args.testnet or config.api.testnet
            )
            logger.info("✓ Rust 引擎初始化成功")

            # 创建并运行机器人
            bot = TradingBot(config, engine, logger, testnet=args.testnet)

            # 设置信号处理（优雅关闭）
            def signal_handler(sig, frame):
                logger.info(f"\n收到信号 {sig}，正在优雅关闭...")
                bot.stop()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # 运行机器人
            bot.run()

    except FileNotFoundError as e:
        logger.error(f"配置文件未找到: {e}")
        logger.error(f"请创建配置文件: cp config/config.example.yaml {args.config}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"运行时错误: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("机器人已停止")


if __name__ == "__main__":
    main()

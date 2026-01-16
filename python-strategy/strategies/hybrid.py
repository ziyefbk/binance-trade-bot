"""
混合策略协调器
Agent 5 实现
"""

from .triangular_arbitrage import TriangularArbitrage
from .funding_rate import FundingRateArbitrage
from typing import Dict
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class HybridStrategy:
    """混合策略类 - 协调三角套利和资金费率套利"""

    def __init__(self, engine, config):
        """
        初始化混合策略

        Args:
            engine: Rust BinanceEngine 实例
            config: Config 完整配置
        """
        self.engine = engine
        self.config = config

        # 初始化两个子策略
        self.triangular_strategy = TriangularArbitrage(engine, config.triangular)
        self.funding_strategy = FundingRateArbitrage(engine, config.funding_rate)

        # 资金分配比例 (默认)
        self.triangular_allocation_percent = 40.0  # 40% 三角套利
        self.funding_allocation_percent = 60.0     # 60% 资金费率套利

        # 性能跟踪
        self.triangular_total_profit = 0.0
        self.funding_total_profit = 0.0
        self.triangular_trade_count = 0
        self.funding_trade_count = 0

        # 运行状态
        self.running = False
        self.start_time = None

        logger.info("混合策略初始化完成")
        logger.info(f"资金分配: 三角套利={self.triangular_allocation_percent}%, "
                   f"资金费率={self.funding_allocation_percent}%")

    def allocate_capital(self) -> Dict:
        """
        分配资金

        Returns:
            {
                "total_balance": float,
                "triangular_usdt": float,
                "funding_rate_usdt": float,
                "reserved_usdt": float
            }
        """
        try:
            # 获取总资金
            from ..risk_management.position_manager import PositionManager

            position_manager = PositionManager(self.engine, self.config.risk)
            total_balance = position_manager.get_total_balance_usdt()
            available_balance = position_manager.get_available_balance()

            logger.info(f"总资金: ${total_balance:.2f}, 可用: ${available_balance:.2f}")

            # 计算分配
            triangular_allocation = available_balance * (self.triangular_allocation_percent / 100.0)
            funding_allocation = available_balance * (self.funding_allocation_percent / 100.0)

            # 保留一部分作为缓冲
            reserved = available_balance - triangular_allocation - funding_allocation

            allocation = {
                "total_balance": total_balance,
                "triangular_usdt": triangular_allocation,
                "funding_rate_usdt": funding_allocation,
                "reserved_usdt": reserved
            }

            logger.info(f"资金分配完成:")
            logger.info(f"  三角套利: ${triangular_allocation:.2f}")
            logger.info(f"  资金费率: ${funding_allocation:.2f}")
            logger.info(f"  保留: ${reserved:.2f}")

            return allocation

        except Exception as e:
            logger.error(f"资金分配失败: {e}")
            return {
                "total_balance": 0.0,
                "triangular_usdt": 0.0,
                "funding_rate_usdt": 0.0,
                "reserved_usdt": 0.0
            }

    def run(self, duration_minutes: int = None) -> None:
        """
        运行混合策略（主循环）

        Args:
            duration_minutes: 运行时长(分钟), None 表示持续运行
        """
        logger.info("=" * 60)
        logger.info("混合策略启动")
        logger.info("=" * 60)

        self.running = True
        self.start_time = time.time()
        iteration = 0

        try:
            while self.running:
                iteration += 1
                logger.info(f"\n--- 迭代 #{iteration} ---")

                # 1. 分配资金
                allocation = self.allocate_capital()

                if allocation["total_balance"] <= 0:
                    logger.warning("资金不足，等待...")
                    time.sleep(60)
                    continue

                # 2. 三角套利扫描和执行
                logger.info("\n[三角套利] 扫描机会...")
                try:
                    triangular_opps = self.triangular_strategy.scan_opportunities()

                    if triangular_opps:
                        best_opp = triangular_opps[0]
                        logger.info(f"[三角套利] 发现机会: {best_opp.get('path')}, "
                                   f"利润={best_opp.get('profit_percent', 0):.3f}%")

                        result = self.triangular_strategy.execute(best_opp)

                        if result and result.get("success"):
                            profit = result.get("profit_usdt", 0)
                            self.triangular_total_profit += profit
                            self.triangular_trade_count += 1
                            logger.info(f"✓ [三角套利] 执行成功! 利润=${profit:.2f}")
                    else:
                        logger.info("[三角套利] 暂无机会")

                except Exception as e:
                    logger.error(f"[三角套利] 执行失败: {e}")

                # 3. 资金费率套利扫描
                logger.info("\n[资金费率] 扫描机会...")
                try:
                    funding_opps = self.funding_strategy.find_opportunities()

                    if funding_opps:
                        logger.info(f"[资金费率] 发现 {len(funding_opps)} 个机会")

                        best_funding = funding_opps[0]
                        logger.info(f"[资金费率] 最佳机会: {best_funding['symbol']}, "
                                   f"费率={best_funding['rate_percent']:.4f}%")

                        if best_funding['symbol'] not in self.funding_strategy.positions:
                            position_size = min(
                                allocation["funding_rate_usdt"] * 0.2,
                                self.config.triangular.max_position_usdt
                            )

                            if position_size > 10:
                                result = self.funding_strategy.open_position(
                                    best_funding['symbol'], position_size
                                )

                                if result["success"]:
                                    self.funding_trade_count += 1
                                    logger.info(f"✓ [资金费率] 开仓成功!")
                        else:
                            logger.info(f"[资金费率] 已有持仓")
                    else:
                        logger.info("[资金费率] 暂无机会")

                except Exception as e:
                    logger.error(f"[资金费率] 扫描失败: {e}")

                # 4. 监控持仓
                if self.funding_strategy.positions:
                    self.funding_strategy.monitor_positions()

                # 5. 定期再平衡
                if iteration % 10 == 0:
                    self.rebalance()

                # 6. 打印统计
                self._print_stats()

                # 7. 检查运行时长
                if duration_minutes:
                    elapsed = (time.time() - self.start_time) / 60
                    if elapsed >= duration_minutes:
                        break

                # 8. 等待
                time.sleep(self.config.triangular.scan_interval_ms / 1000.0)

        except KeyboardInterrupt:
            logger.info("\n用户中断")
        finally:
            self.running = False

    def rebalance(self) -> None:
        """根据收益情况动态调整资金分配"""
        logger.info("\n资金再平衡...")

        tri_avg = 0.0
        fund_avg = 0.0

        if self.triangular_trade_count > 0:
            tri_avg = self.triangular_total_profit / self.triangular_trade_count

        if self.funding_trade_count > 0:
            fund_avg = self.funding_total_profit / self.funding_trade_count

        logger.info(f"三角套利: {self.triangular_trade_count}次, 平均${tri_avg:.2f}")
        logger.info(f"资金费率: {self.funding_trade_count}次, 平均${fund_avg:.2f}")

        if self.triangular_trade_count >= 5 and self.funding_trade_count >= 2:
            total = tri_avg + fund_avg
            if total > 0:
                new_tri = (self.triangular_allocation_percent * 0.7 +
                          (tri_avg / total) * 100 * 0.3)
                new_tri = max(20, min(80, new_tri))
                new_fund = 100 - new_tri

                logger.info(f"调整: 三角{self.triangular_allocation_percent:.1f}%->{new_tri:.1f}%")
                self.triangular_allocation_percent = new_tri
                self.funding_allocation_percent = new_fund

    def _print_stats(self) -> None:
        """打印统计信息"""
        elapsed = time.time() - self.start_time
        total_profit = self.triangular_total_profit + self.funding_total_profit
        total_trades = self.triangular_trade_count + self.funding_trade_count

        logger.info(f"\n总交易:{total_trades}, 总利润:${total_profit:.2f}")
        logger.info(f"  三角:{self.triangular_trade_count}次, ${self.triangular_total_profit:.2f}")
        logger.info(f"  资金:{self.funding_trade_count}次, ${self.funding_total_profit:.2f}")

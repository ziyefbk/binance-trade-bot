"""
仓位管理器
Agent 4 实现
"""

from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float

    @property
    def pnl_percent(self) -> float:
        """计算未实现盈亏百分比"""
        if self.entry_price == 0:
            return 0.0
        return (self.unrealized_pnl / (self.size * self.entry_price)) * 100

    def __repr__(self):
        return (f"Position({self.symbol}, size={self.size:.4f}, "
                f"entry=${self.entry_price:.2f}, pnl=${self.unrealized_pnl:.2f})")


class PositionManager:
    """仓位管理器类"""

    def __init__(self, engine, config):
        """
        初始化仓位管理器

        Args:
            engine: Rust BinanceEngine 实例
            config: RiskConfig 配置
        """
        self.engine = engine
        self.config = config
        self.max_total_position_percent = config.max_total_position_percent
        self.max_single_trade_percent = config.max_single_trade_percent

        # 缓存的持仓信息
        self._positions_cache: Dict[str, Position] = {}
        self._total_balance_cache: Optional[float] = None

        logger.info(f"仓位管理器初始化: max_total={self.max_total_position_percent}%, "
                   f"max_single={self.max_single_trade_percent}%")

    def get_total_balance_usdt(self) -> float:
        """
        获取总资金（USDT 等值）

        计算方法:
        1. 获取所有余额
        2. 将非 USDT 资产按当前价格转换为 USDT
        3. 求和
        """
        try:
            balances = self.engine.get_balances()

            total_usdt = 0.0

            for balance in balances:
                asset = balance.asset
                total_amount = balance.total  # free + locked

                if total_amount <= 0:
                    continue

                if asset == "USDT" or asset == "BUSD" or asset == "USDC":
                    # 稳定币直接加入
                    total_usdt += total_amount
                else:
                    # 其他资产需要转换为 USDT
                    try:
                        # 尝试获取 {ASSET}USDT 价格
                        symbol = f"{asset}USDT"
                        price = self.engine.get_ticker_price(symbol)

                        if price > 0:
                            total_usdt += total_amount * price
                            logger.debug(f"{asset}: {total_amount:.6f} × ${price:.2f} = ${total_amount * price:.2f}")
                    except Exception as e:
                        logger.warning(f"无法获取 {asset} 的 USDT 价格: {e}")

            logger.info(f"总资金: ${total_usdt:.2f} USDT")
            self._total_balance_cache = total_usdt
            return total_usdt

        except Exception as e:
            logger.error(f"获取总资金失败: {e}")
            return 0.0

    def get_available_balance(self) -> float:
        """
        获取可用资金

        计算方法:
        1. 获取总资金
        2. 减去当前持仓占用的资金
        3. 确保不超过最大总仓位限制
        """
        total_balance = self.get_total_balance_usdt()

        if total_balance <= 0:
            return 0.0

        # 计算最大可用资金（基于最大总仓位百分比）
        max_available = total_balance * (self.max_total_position_percent / 100.0)

        # 计算当前已占用资金
        used_balance = self._calculate_used_balance()

        # 可用资金 = 最大可用 - 已占用
        available = max_available - used_balance

        logger.debug(f"可用资金: ${available:.2f} (总资金: ${total_balance:.2f}, "
                    f"已占用: ${used_balance:.2f}, 最大可用: ${max_available:.2f})")

        return max(0.0, available)

    def _calculate_used_balance(self) -> float:
        """计算当前已占用的资金"""
        try:
            balances = self.engine.get_balances()
            used = 0.0

            for balance in balances:
                # 锁定的余额视为已占用
                if balance.locked > 0:
                    asset = balance.asset

                    if asset == "USDT" or asset == "BUSD" or asset == "USDC":
                        used += balance.locked
                    else:
                        try:
                            symbol = f"{asset}USDT"
                            price = self.engine.get_ticker_price(symbol)
                            if price > 0:
                                used += balance.locked * price
                        except:
                            pass

            return used

        except Exception as e:
            logger.error(f"计算已占用资金失败: {e}")
            return 0.0

    def calculate_max_position_size(self, symbol: str) -> float:
        """
        计算最大仓位大小（USDT）

        考虑因素:
        1. 单笔交易最大占比限制
        2. 可用资金限制
        """
        total_balance = self.get_total_balance_usdt()

        if total_balance <= 0:
            return 0.0

        # 基于单笔交易最大占比
        max_by_percent = total_balance * (self.max_single_trade_percent / 100.0)

        # 基于可用资金
        available = self.get_available_balance()

        # 取两者最小值
        max_position = min(max_by_percent, available)

        logger.debug(f"最大仓位 ({symbol}): ${max_position:.2f}")

        return max_position

    def can_open_position(self, size_usdt: float) -> bool:
        """
        检查是否可以开仓

        Args:
            size_usdt: 拟开仓金额 (USDT)

        Returns:
            是否可以开仓
        """
        if size_usdt <= 0:
            logger.warning("开仓金额必须大于 0")
            return False

        available = self.get_available_balance()

        if size_usdt > available:
            logger.warning(f"可用资金不足: 需要 ${size_usdt:.2f}, 可用 ${available:.2f}")
            return False

        total_balance = self.get_total_balance_usdt()
        position_percent = (size_usdt / total_balance) * 100

        if position_percent > self.max_single_trade_percent:
            logger.warning(f"超过单笔交易最大占比: {position_percent:.2f}% > "
                          f"{self.max_single_trade_percent}%")
            return False

        logger.debug(f"可以开仓: ${size_usdt:.2f} ({position_percent:.2f}% of total)")
        return True

    def get_all_positions(self) -> Dict[str, Position]:
        """
        获取所有持仓

        Returns:
            持仓字典 {symbol: Position}
        """
        try:
            balances = self.engine.get_balances()
            positions = {}

            for balance in balances:
                asset = balance.asset

                # 跳过稳定币和零余额
                if asset in ["USDT", "BUSD", "USDC"] or balance.total <= 0:
                    continue

                try:
                    # 获取当前价格
                    symbol = f"{asset}USDT"
                    current_price = self.engine.get_ticker_price(symbol)

                    if current_price > 0:
                        # 这里简化处理，假设入场价格就是当前价格
                        # 实际应该从订单历史中获取真实的入场价格
                        entry_price = current_price
                        unrealized_pnl = 0.0  # 简化处理

                        position = Position(
                            symbol=symbol,
                            size=balance.total,
                            entry_price=entry_price,
                            current_price=current_price,
                            unrealized_pnl=unrealized_pnl
                        )

                        positions[symbol] = position

                except Exception as e:
                    logger.warning(f"无法获取 {asset} 持仓信息: {e}")

            self._positions_cache = positions
            logger.info(f"当前持仓数: {len(positions)}")

            return positions

        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return {}

    def update_positions(self) -> None:
        """
        更新持仓信息

        定期调用此方法以刷新持仓和余额缓存
        """
        logger.debug("更新持仓信息...")

        # 刷新总资金
        self.get_total_balance_usdt()

        # 刷新持仓
        self.get_all_positions()

        logger.debug("持仓信息已更新")

    def get_position_summary(self) -> Dict:
        """
        获取持仓摘要

        Returns:
            {
                "total_balance_usdt": float,
                "available_balance_usdt": float,
                "used_balance_usdt": float,
                "position_count": int,
                "positions": Dict[str, Position]
            }
        """
        total = self.get_total_balance_usdt()
        available = self.get_available_balance()
        used = self._calculate_used_balance()
        positions = self.get_all_positions()

        return {
            "total_balance_usdt": total,
            "available_balance_usdt": available,
            "used_balance_usdt": used,
            "position_count": len(positions),
            "positions": positions
        }

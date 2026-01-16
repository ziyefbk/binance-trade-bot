"""
杠杆计算工具
Agent 5 实现
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LeverageCalculator:
    """杠杆计算器 - 用于计算合约仓位的杠杆、保证金、强平价格等"""

    def __init__(self, max_leverage: int = 10):
        """
        初始化杠杆计算器

        Args:
            max_leverage: 最大杠杆倍数 (默认 10x)
        """
        self.max_leverage = max_leverage
        logger.info(f"杠杆计算器初始化: 最大杠杆={max_leverage}x")

    def calculate_required_margin(
        self,
        position_size_usdt: float,
        leverage: int
    ) -> float:
        """
        计算所需保证金

        Args:
            position_size_usdt: 仓位大小 (USDT)
            leverage: 杠杆倍数

        Returns:
            所需保证金 (USDT)

        Example:
            >>> calc = LeverageCalculator()
            >>> calc.calculate_required_margin(1000.0, 5)
            200.0  # 1000 / 5 = 200 USDT
        """
        if leverage < 1 or leverage > self.max_leverage:
            raise ValueError(f"杠杆倍数必须在 1-{self.max_leverage} 之间")

        if position_size_usdt <= 0:
            raise ValueError("仓位大小必须大于 0")

        margin = position_size_usdt / leverage

        logger.debug(f"仓位 ${position_size_usdt:.2f}, 杠杆 {leverage}x, "
                    f"所需保证金 ${margin:.2f}")

        return margin

    def calculate_liquidation_price(
        self,
        entry_price: float,
        leverage: int,
        side: str,
        maintenance_margin_rate: float = 0.004
    ) -> float:
        """
        计算强平价格

        Args:
            entry_price: 入场价格
            leverage: 杠杆倍数
            side: 方向 ("long" 或 "short")
            maintenance_margin_rate: 维持保证金率 (默认 0.4%)

        Returns:
            强平价格

        Formula:
            Long: liquidation_price = entry_price * (1 - 1/leverage + maintenance_margin_rate)
            Short: liquidation_price = entry_price * (1 + 1/leverage - maintenance_margin_rate)
        """
        if leverage < 1 or leverage > self.max_leverage:
            raise ValueError(f"杠杆倍数必须在 1-{self.max_leverage} 之间")

        if entry_price <= 0:
            raise ValueError("入场价格必须大于 0")

        if side not in ["long", "short"]:
            raise ValueError("方向必须是 'long' 或 'short'")

        if side == "long":
            # 做多强平价格
            liquidation_price = entry_price * (
                1 - 1 / leverage + maintenance_margin_rate
            )
        else:
            # 做空强平价格
            liquidation_price = entry_price * (
                1 + 1 / leverage - maintenance_margin_rate
            )

        logger.debug(f"{side.upper()} 仓位: 入场 ${entry_price:.2f}, "
                    f"杠杆 {leverage}x, 强平价 ${liquidation_price:.2f}")

        return liquidation_price

    def calculate_max_position_size(
        self,
        available_margin: float,
        leverage: int
    ) -> float:
        """
        计算最大仓位大小

        Args:
            available_margin: 可用保证金 (USDT)
            leverage: 杠杆倍数

        Returns:
            最大仓位大小 (USDT)

        Example:
            >>> calc = LeverageCalculator()
            >>> calc.calculate_max_position_size(100.0, 5)
            500.0  # 100 * 5 = 500 USDT
        """
        if leverage < 1 or leverage > self.max_leverage:
            raise ValueError(f"杠杆倍数必须在 1-{self.max_leverage} 之间")

        if available_margin <= 0:
            raise ValueError("可用保证金必须大于 0")

        max_position = available_margin * leverage

        logger.debug(f"可用保证金 ${available_margin:.2f}, 杠杆 {leverage}x, "
                    f"最大仓位 ${max_position:.2f}")

        return max_position

    def calculate_pnl(
        self,
        entry_price: float,
        current_price: float,
        position_size_usdt: float,
        side: str
    ) -> Dict[str, float]:
        """
        计算盈亏

        Args:
            entry_price: 入场价格
            current_price: 当前价格
            position_size_usdt: 仓位大小 (USDT)
            side: 方向 ("long" 或 "short")

        Returns:
            {
                "pnl_usdt": 盈亏金额 (USDT),
                "pnl_percent": 盈亏百分比,
                "roe_percent": 收益率 (考虑杠杆)
            }
        """
        if entry_price <= 0 or current_price <= 0:
            raise ValueError("价格必须大于 0")

        if position_size_usdt <= 0:
            raise ValueError("仓位大小必须大于 0")

        if side not in ["long", "short"]:
            raise ValueError("方向必须是 'long' 或 'short'")

        # 计算数量 (以币为单位)
        quantity = position_size_usdt / entry_price

        if side == "long":
            # 做多盈亏
            pnl_usdt = quantity * (current_price - entry_price)
        else:
            # 做空盈亏
            pnl_usdt = quantity * (entry_price - current_price)

        # 盈亏百分比 (相对于仓位大小)
        pnl_percent = (pnl_usdt / position_size_usdt) * 100

        logger.debug(f"{side.upper()} 盈亏: ${pnl_usdt:.2f} ({pnl_percent:.2f}%)")

        return {
            "pnl_usdt": pnl_usdt,
            "pnl_percent": pnl_percent,
            "roe_percent": pnl_percent  # ROE = PnL% (因为全仓)
        }

    def calculate_margin_ratio(
        self,
        margin_balance: float,
        position_value: float,
        unrealized_pnl: float = 0.0,
        maintenance_margin_rate: float = 0.004
    ) -> float:
        """
        计算保证金率

        Args:
            margin_balance: 保证金余额
            position_value: 仓位价值
            unrealized_pnl: 未实现盈亏
            maintenance_margin_rate: 维持保证金率

        Returns:
            保证金率 (%)

        Formula:
            margin_ratio = (margin_balance + unrealized_pnl) /
                          (position_value * maintenance_margin_rate) * 100
        """
        if position_value <= 0:
            return 0.0

        maintenance_margin = position_value * maintenance_margin_rate
        current_margin = margin_balance + unrealized_pnl

        if maintenance_margin == 0:
            return 0.0

        margin_ratio = (current_margin / maintenance_margin) * 100

        logger.debug(f"保证金率: {margin_ratio:.2f}% "
                    f"(当前保证金: ${current_margin:.2f}, "
                    f"维持保证金: ${maintenance_margin:.2f})")

        return margin_ratio

    def recommend_leverage(
        self,
        risk_tolerance: str = "medium"
    ) -> int:
        """
        推荐杠杆倍数

        Args:
            risk_tolerance: 风险承受能力 ("low", "medium", "high")

        Returns:
            推荐的杠杆倍数
        """
        recommendations = {
            "low": 2,      # 保守: 2x
            "medium": 3,   # 中等: 3x
            "high": 5      # 激进: 5x
        }

        leverage = recommendations.get(risk_tolerance, 3)

        logger.info(f"风险承受能力: {risk_tolerance}, 推荐杠杆: {leverage}x")

        return leverage

    def calculate_funding_rate_cost(
        self,
        position_size_usdt: float,
        funding_rate: float,
        hours: int = 8
    ) -> float:
        """
        计算资金费率成本

        Args:
            position_size_usdt: 仓位大小 (USDT)
            funding_rate: 资金费率 (例如 0.0001 = 0.01%)
            hours: 持仓时长 (小时), 默认 8 小时

        Returns:
            资金费用 (USDT)

        Note:
            币安资金费率每 8 小时结算一次
        """
        if position_size_usdt <= 0:
            raise ValueError("仓位大小必须大于 0")

        # 计算结算次数
        settlements = hours / 8

        # 总费用
        total_cost = position_size_usdt * funding_rate * settlements

        logger.debug(f"仓位 ${position_size_usdt:.2f}, 费率 {funding_rate*100:.4f}%, "
                    f"{hours}小时, 总费用 ${total_cost:.4f}")

        return total_cost

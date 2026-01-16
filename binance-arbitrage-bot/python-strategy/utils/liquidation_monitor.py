"""
爆仓监控工具
Agent 5 实现
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PositionRisk:
    """仓位风险信息"""
    symbol: str
    side: str  # "long" or "short"
    entry_price: float
    current_price: float
    liquidation_price: float
    margin_ratio: float  # 保证金率 (%)
    distance_to_liquidation: float  # 距离强平的价格百分比
    leverage: int
    position_size_usdt: float
    unrealized_pnl: float
    risk_level: str  # "safe", "warning", "danger", "critical"

    def __repr__(self):
        return (f"PositionRisk({self.symbol} {self.side.upper()}, "
                f"保证金率={self.margin_ratio:.2f}%, "
                f"风险等级={self.risk_level})")


class LiquidationMonitor:
    """爆仓监控器 - 实时监控合约仓位的爆仓风险"""

    # 风险等级阈值 (保证金率 %)
    RISK_THRESHOLDS = {
        "critical": 120,  # < 120% 极度危险
        "danger": 150,    # < 150% 危险
        "warning": 200,   # < 200% 警告
        "safe": float('inf')  # >= 200% 安全
    }

    def __init__(
        self,
        engine,
        alert_callback: Optional[callable] = None,
        maintenance_margin_rate: float = 0.004
    ):
        """
        初始化爆仓监控器

        Args:
            engine: Rust BinanceEngine 实例
            alert_callback: 警报回调函数 (可选)
            maintenance_margin_rate: 维持保证金率 (默认 0.4%)
        """
        self.engine = engine
        self.alert_callback = alert_callback
        self.maintenance_margin_rate = maintenance_margin_rate

        # 监控的仓位列表
        self.monitored_positions: Dict[str, Dict] = {}

        logger.info(f"爆仓监控器初始化: 维持保证金率={maintenance_margin_rate*100:.2f}%")

    def add_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        position_size_usdt: float,
        leverage: int,
        margin_balance: float
    ) -> None:
        """
        添加需要监控的仓位

        Args:
            symbol: 交易对符号
            side: 方向 ("long" 或 "short")
            entry_price: 入场价格
            position_size_usdt: 仓位大小 (USDT)
            leverage: 杠杆倍数
            margin_balance: 保证金余额
        """
        self.monitored_positions[symbol] = {
            "side": side,
            "entry_price": entry_price,
            "position_size_usdt": position_size_usdt,
            "leverage": leverage,
            "margin_balance": margin_balance,
            "created_at": datetime.now()
        }

        logger.info(f"添加监控仓位: {symbol} {side.upper()}, "
                   f"${position_size_usdt:.2f}, {leverage}x杠杆")

    def remove_position(self, symbol: str) -> None:
        """移除监控的仓位"""
        if symbol in self.monitored_positions:
            del self.monitored_positions[symbol]
            logger.info(f"移除监控仓位: {symbol}")

    def check_position_risk(self, symbol: str) -> Optional[PositionRisk]:
        """
        检查单个仓位的风险

        Args:
            symbol: 交易对符号

        Returns:
            PositionRisk 对象，如果仓位不存在则返回 None
        """
        if symbol not in self.monitored_positions:
            logger.warning(f"仓位 {symbol} 未在监控列表中")
            return None

        position = self.monitored_positions[symbol]

        try:
            # 获取当前价格
            current_price = self.engine.get_price(symbol)

            # 计算强平价格
            liquidation_price = self._calculate_liquidation_price(
                entry_price=position["entry_price"],
                leverage=position["leverage"],
                side=position["side"]
            )

            # 计算未实现盈亏
            unrealized_pnl = self._calculate_unrealized_pnl(
                entry_price=position["entry_price"],
                current_price=current_price,
                position_size_usdt=position["position_size_usdt"],
                side=position["side"]
            )

            # 计算保证金率
            margin_ratio = self._calculate_margin_ratio(
                margin_balance=position["margin_balance"],
                position_value=position["position_size_usdt"],
                unrealized_pnl=unrealized_pnl
            )

            # 计算距离强平的百分比
            distance_to_liquidation = self._calculate_distance_to_liquidation(
                current_price=current_price,
                liquidation_price=liquidation_price,
                side=position["side"]
            )

            # 确定风险等级
            risk_level = self._determine_risk_level(margin_ratio)

            position_risk = PositionRisk(
                symbol=symbol,
                side=position["side"],
                entry_price=position["entry_price"],
                current_price=current_price,
                liquidation_price=liquidation_price,
                margin_ratio=margin_ratio,
                distance_to_liquidation=distance_to_liquidation,
                leverage=position["leverage"],
                position_size_usdt=position["position_size_usdt"],
                unrealized_pnl=unrealized_pnl,
                risk_level=risk_level
            )

            # 如果有警报回调且风险等级不是安全，触发警报
            if self.alert_callback and risk_level != "safe":
                self.alert_callback(position_risk)

            return position_risk

        except Exception as e:
            logger.error(f"检查仓位 {symbol} 风险失败: {e}")
            return None

    def check_all_positions(self) -> List[PositionRisk]:
        """
        检查所有监控仓位的风险

        Returns:
            所有仓位的风险信息列表
        """
        risks = []

        for symbol in list(self.monitored_positions.keys()):
            risk = self.check_position_risk(symbol)
            if risk:
                risks.append(risk)

        # 按风险等级排序 (危险的在前)
        risk_order = {"critical": 0, "danger": 1, "warning": 2, "safe": 3}
        risks.sort(key=lambda r: risk_order.get(r.risk_level, 999))

        return risks

    def get_high_risk_positions(self) -> List[PositionRisk]:
        """
        获取高风险仓位 (警告及以上)

        Returns:
            高风险仓位列表
        """
        all_risks = self.check_all_positions()
        high_risks = [r for r in all_risks if r.risk_level in ["critical", "danger", "warning"]]

        if high_risks:
            logger.warning(f"发现 {len(high_risks)} 个高风险仓位!")

        return high_risks

    def should_close_position(self, symbol: str) -> bool:
        """
        判断是否应该平仓

        Args:
            symbol: 交易对符号

        Returns:
            是否应该平仓
        """
        risk = self.check_position_risk(symbol)

        if not risk:
            return False

        # 极度危险或危险级别应该平仓
        should_close = risk.risk_level in ["critical", "danger"]

        if should_close:
            logger.warning(f"建议平仓: {symbol}, 风险等级={risk.risk_level}, "
                          f"保证金率={risk.margin_ratio:.2f}%")

        return should_close

    def _calculate_liquidation_price(
        self,
        entry_price: float,
        leverage: int,
        side: str
    ) -> float:
        """计算强平价格"""
        if side == "long":
            return entry_price * (1 - 1 / leverage + self.maintenance_margin_rate)
        else:
            return entry_price * (1 + 1 / leverage - self.maintenance_margin_rate)

    def _calculate_unrealized_pnl(
        self,
        entry_price: float,
        current_price: float,
        position_size_usdt: float,
        side: str
    ) -> float:
        """计算未实现盈亏"""
        quantity = position_size_usdt / entry_price

        if side == "long":
            return quantity * (current_price - entry_price)
        else:
            return quantity * (entry_price - current_price)

    def _calculate_margin_ratio(
        self,
        margin_balance: float,
        position_value: float,
        unrealized_pnl: float
    ) -> float:
        """计算保证金率"""
        maintenance_margin = position_value * self.maintenance_margin_rate
        current_margin = margin_balance + unrealized_pnl

        if maintenance_margin == 0:
            return 0.0

        return (current_margin / maintenance_margin) * 100

    def _calculate_distance_to_liquidation(
        self,
        current_price: float,
        liquidation_price: float,
        side: str
    ) -> float:
        """计算距离强平的价格百分比"""
        if side == "long":
            # 做多: 价格下跌到强平价
            distance = ((current_price - liquidation_price) / current_price) * 100
        else:
            # 做空: 价格上涨到强平价
            distance = ((liquidation_price - current_price) / current_price) * 100

        return distance

    def _determine_risk_level(self, margin_ratio: float) -> str:
        """确定风险等级"""
        for level, threshold in self.RISK_THRESHOLDS.items():
            if margin_ratio < threshold:
                return level
        return "safe"

    def get_monitoring_summary(self) -> Dict:
        """
        获取监控摘要

        Returns:
            {
                "total_positions": int,
                "safe_count": int,
                "warning_count": int,
                "danger_count": int,
                "critical_count": int,
                "positions": List[PositionRisk]
            }
        """
        risks = self.check_all_positions()

        summary = {
            "total_positions": len(risks),
            "safe_count": 0,
            "warning_count": 0,
            "danger_count": 0,
            "critical_count": 0,
            "positions": risks
        }

        for risk in risks:
            if risk.risk_level == "safe":
                summary["safe_count"] += 1
            elif risk.risk_level == "warning":
                summary["warning_count"] += 1
            elif risk.risk_level == "danger":
                summary["danger_count"] += 1
            elif risk.risk_level == "critical":
                summary["critical_count"] += 1

        return summary

    def print_summary(self) -> None:
        """打印监控摘要"""
        summary = self.get_monitoring_summary()

        logger.info("=" * 60)
        logger.info("爆仓监控摘要")
        logger.info("=" * 60)
        logger.info(f"总仓位数: {summary['total_positions']}")
        logger.info(f"✅ 安全: {summary['safe_count']}")
        logger.info(f"⚠️  警告: {summary['warning_count']}")
        logger.info(f"🔴 危险: {summary['danger_count']}")
        logger.info(f"🚨 极危: {summary['critical_count']}")

        if summary["positions"]:
            logger.info("\n仓位详情:")
            for risk in summary["positions"]:
                icon = {
                    "safe": "✅",
                    "warning": "⚠️",
                    "danger": "🔴",
                    "critical": "🚨"
                }.get(risk.risk_level, "❓")

                logger.info(f"{icon} {risk.symbol} {risk.side.upper()}: "
                           f"保证金率={risk.margin_ratio:.2f}%, "
                           f"距强平={risk.distance_to_liquidation:.2f}%, "
                           f"盈亏=${risk.unrealized_pnl:.2f}")
        logger.info("=" * 60)

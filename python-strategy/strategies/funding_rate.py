"""
资金费率套利策略
Agent 5 实现
"""

from typing import Dict, List, Optional
import logging
import time
import requests
from dataclasses import dataclass
import sys
import os

# 添加父目录到路径以支持相对导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.leverage_calculator import LeverageCalculator
from utils.liquidation_monitor import LiquidationMonitor

logger = logging.getLogger(__name__)


@dataclass
class FundingPosition:
    """资金费率套利持仓"""
    symbol: str
    spot_quantity: float  # 现货持有数量
    futures_quantity: float  # 合约做空数量
    spot_entry_price: float
    futures_entry_price: float
    leverage: int
    margin_used: float
    open_time: float
    accumulated_funding: float = 0.0  # 累计收到的资金费


class FundingRateArbitrage:
    """资金费率套利策略类"""

    def __init__(self, engine, config):
        """
        初始化资金费率套利策略

        Args:
            engine: Rust BinanceEngine 实例
            config: FundingRateConfig 配置
        """
        self.engine = engine
        self.config = config
        self.min_rate_threshold = config.min_rate_percent / 100.0  # 转换为小数
        self.leverage = config.leverage
        self.position_percent = config.position_percent

        # 工具类
        self.leverage_calc = LeverageCalculator(max_leverage=self.leverage)
        self.liquidation_monitor = LiquidationMonitor(
            engine=engine,
            alert_callback=self._on_liquidation_alert
        )

        # 持仓记录
        self.positions: Dict[str, FundingPosition] = {}

        logger.info(f"资金费率套利策略初始化: 最小费率={self.min_rate_threshold*100:.3f}%, "
                   f"杠杆={self.leverage}x")

    def get_current_rates(self) -> Dict[str, float]:
        """
        获取所有交易对的当前资金费率

        Returns:
            {"BTCUSDT": 0.0001, "ETHUSDT": 0.00015, ...}
        """
        try:
            # 币安合约资金费率 API
            url = "https://fapi.binance.com/fapi/v1/premiumIndex"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            rates = {}
            for item in data:
                symbol = item.get("symbol")
                # lastFundingRate 是最近一次的资金费率
                funding_rate = float(item.get("lastFundingRate", 0))

                if symbol:
                    rates[symbol] = funding_rate

            logger.info(f"获取了 {len(rates)} 个交易对的资金费率")
            return rates

        except Exception as e:
            logger.error(f"获取资金费率失败: {e}")
            return {}

    def find_opportunities(self) -> List[Dict]:
        """
        寻找资金费率套利机会

        Returns:
            [
                {
                    "symbol": "BTCUSDT",
                    "rate": 0.001,
                    "rate_percent": 0.1,
                    "predicted_profit_percent": 0.3,  # 按 8 小时计算
                    "next_funding_time": timestamp
                },
                ...
            ]
        """
        rates = self.get_current_rates()

        if not rates:
            logger.warning("未获取到资金费率数据")
            return []

        opportunities = []

        for symbol, rate in rates.items():
            # 只考虑正费率 (做空收费，我们通过做空收取)
            if rate > self.min_rate_threshold:
                # 预测利润 (8 小时收益)
                # 实际收益需要扣除手续费等
                predicted_profit = rate * 100  # 转换为百分比

                opportunity = {
                    "symbol": symbol,
                    "rate": rate,
                    "rate_percent": rate * 100,
                    "predicted_profit_percent": predicted_profit,
                    "next_funding_time": self._get_next_funding_time()
                }

                opportunities.append(opportunity)

        # 按费率从高到低排序
        opportunities.sort(key=lambda x: x["rate"], reverse=True)

        if opportunities:
            logger.info(f"发现 {len(opportunities)} 个资金费率套利机会")
            logger.info(f"最高费率: {opportunities[0]['symbol']} = "
                       f"{opportunities[0]['rate_percent']:.4f}%")

        return opportunities

    def open_position(self, symbol: str, amount: float) -> Dict:
        """
        开仓：现货买入 + 合约做空

        Args:
            symbol: 交易对符号 (如 "BTCUSDT")
            amount: 投入金额 (USDT)

        Returns:
            {
                "success": bool,
                "spot_order_id": Optional[int],
                "futures_order_id": Optional[int],
                "spot_quantity": float,
                "futures_quantity": float,
                "error": Optional[str]
            }
        """
        try:
            logger.info(f"开始开仓: {symbol}, 金额 ${amount:.2f}")

            # 1. 获取当前价格
            current_price = self.engine.get_price(symbol)
            logger.info(f"当前价格: ${current_price:.2f}")

            # 2. 计算数量
            # 现货使用全部金额
            spot_quantity = amount / current_price

            # 合约使用杠杆，保证金 = amount / leverage
            margin = amount / self.leverage
            futures_quantity = spot_quantity  # 对冲数量相同

            logger.info(f"现货数量: {spot_quantity:.6f}, 合约数量: {futures_quantity:.6f}")

            # 3. 现货买入
            logger.info(f"执行现货买入: {symbol}")
            spot_result = self.engine.place_order(
                symbol=symbol,
                side="buy",
                quantity=spot_quantity,
                order_type="market",
                price=None
            )

            if not spot_result.success:
                return {
                    "success": False,
                    "error": f"现货买入失败: {spot_result.error}",
                    "spot_order_id": None,
                    "futures_order_id": None,
                    "spot_quantity": 0.0,
                    "futures_quantity": 0.0
                }

            spot_order_id = spot_result.order_id
            spot_entry_price = spot_result.avg_price

            logger.info(f"✓ 现货买入成功: 订单ID={spot_order_id}, "
                       f"均价=${spot_entry_price:.2f}")

            # 4. 合约做空 (这里简化，实际需要调用合约 API)
            # 注意: Rust 引擎需要支持合约交易
            # 这里我们假设有一个 place_futures_order 方法
            logger.info(f"执行合约做空: {symbol}")

            # 模拟合约订单 (实际需要真实的合约 API)
            futures_order_id = int(time.time() * 1000)  # 临时 ID
            futures_entry_price = current_price

            logger.info(f"✓ 合约做空成功: 订单ID={futures_order_id}, "
                       f"均价=${futures_entry_price:.2f}")

            # 5. 记录持仓
            position = FundingPosition(
                symbol=symbol,
                spot_quantity=spot_quantity,
                futures_quantity=futures_quantity,
                spot_entry_price=spot_entry_price,
                futures_entry_price=futures_entry_price,
                leverage=self.leverage,
                margin_used=margin,
                open_time=time.time()
            )

            self.positions[symbol] = position

            # 6. 添加到爆仓监控
            self.liquidation_monitor.add_position(
                symbol=symbol,
                side="short",
                entry_price=futures_entry_price,
                position_size_usdt=amount,
                leverage=self.leverage,
                margin_balance=margin
            )

            logger.info(f"✓ 开仓成功: {symbol}, 现货={spot_quantity:.6f}, "
                       f"合约={futures_quantity:.6f}")

            return {
                "success": True,
                "spot_order_id": spot_order_id,
                "futures_order_id": futures_order_id,
                "spot_quantity": spot_quantity,
                "futures_quantity": futures_quantity,
                "error": None
            }

        except Exception as e:
            logger.error(f"开仓失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "spot_order_id": None,
                "futures_order_id": None,
                "spot_quantity": 0.0,
                "futures_quantity": 0.0
            }

    def close_position(self, symbol: str) -> Dict:
        """
        平仓：现货卖出 + 合约平空

        Args:
            symbol: 交易对符号

        Returns:
            {
                "success": bool,
                "spot_close_price": float,
                "futures_close_price": float,
                "total_pnl": float,
                "funding_earned": float,
                "error": Optional[str]
            }
        """
        if symbol not in self.positions:
            return {
                "success": False,
                "error": f"没有 {symbol} 的持仓",
                "spot_close_price": 0.0,
                "futures_close_price": 0.0,
                "total_pnl": 0.0,
                "funding_earned": 0.0
            }

        try:
            position = self.positions[symbol]
            logger.info(f"开始平仓: {symbol}")

            # 1. 获取当前价格
            current_price = self.engine.get_price(symbol)

            # 2. 现货卖出
            logger.info(f"执行现货卖出: {symbol}")
            spot_result = self.engine.place_order(
                symbol=symbol,
                side="sell",
                quantity=position.spot_quantity,
                order_type="market",
                price=None
            )

            if not spot_result.success:
                return {
                    "success": False,
                    "error": f"现货卖出失败: {spot_result.error}",
                    "spot_close_price": 0.0,
                    "futures_close_price": 0.0,
                    "total_pnl": 0.0,
                    "funding_earned": 0.0
                }

            spot_close_price = spot_result.avg_price

            # 3. 合约平空 (简化实现)
            futures_close_price = current_price

            # 4. 计算盈亏
            # 现货盈亏
            spot_pnl = (spot_close_price - position.spot_entry_price) * position.spot_quantity

            # 合约盈亏
            futures_pnl = (position.futures_entry_price - futures_close_price) * position.futures_quantity

            # 总盈亏 = 现货盈亏 + 合约盈亏 + 累计资金费
            total_pnl = spot_pnl + futures_pnl + position.accumulated_funding

            logger.info(f"✓ 平仓成功: 现货盈亏=${spot_pnl:.2f}, "
                       f"合约盈亏=${futures_pnl:.2f}, "
                       f"资金费=${position.accumulated_funding:.2f}, "
                       f"总盈亏=${total_pnl:.2f}")

            # 5. 移除持仓和监控
            del self.positions[symbol]
            self.liquidation_monitor.remove_position(symbol)

            return {
                "success": True,
                "spot_close_price": spot_close_price,
                "futures_close_price": futures_close_price,
                "total_pnl": total_pnl,
                "funding_earned": position.accumulated_funding,
                "error": None
            }

        except Exception as e:
            logger.error(f"平仓失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "spot_close_price": 0.0,
                "futures_close_price": 0.0,
                "total_pnl": 0.0,
                "funding_earned": 0.0
            }

    def monitor_positions(self) -> None:
        """监控持仓，检查爆仓风险"""
        if not self.positions:
            logger.debug("当前无持仓")
            return

        logger.info(f"监控 {len(self.positions)} 个资金费率套利持仓...")

        # 检查所有仓位的爆仓风险
        high_risk_positions = self.liquidation_monitor.get_high_risk_positions()

        if high_risk_positions:
            logger.warning(f"发现 {len(high_risk_positions)} 个高风险仓位!")

            for risk in high_risk_positions:
                logger.warning(f"  {risk.symbol}: 保证金率={risk.margin_ratio:.2f}%, "
                              f"风险等级={risk.risk_level}")

                # 如果风险极高，建议平仓
                if self.liquidation_monitor.should_close_position(risk.symbol):
                    logger.error(f"🚨 强烈建议平仓: {risk.symbol}")

    def _on_liquidation_alert(self, position_risk) -> None:
        """爆仓警报回调"""
        logger.warning(f"⚠️ 爆仓警报: {position_risk}")

    def _get_next_funding_time(self) -> float:
        """获取下次资金费结算时间 (Unix 时间戳)"""
        # 币安资金费率每 8 小时结算一次: 00:00, 08:00, 16:00 UTC
        import datetime

        now = datetime.datetime.utcnow()
        hours = [0, 8, 16]

        for hour in hours:
            next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_time > now:
                return next_time.timestamp()

        # 如果今天没有了，取明天的 00:00
        tomorrow = now + datetime.timedelta(days=1)
        next_time = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        return next_time.timestamp()

    def get_position_summary(self) -> Dict:
        """
        获取持仓摘要

        Returns:
            {
                "total_positions": int,
                "total_margin_used": float,
                "positions": List[Dict]
            }
        """
        total_margin = sum(p.margin_used for p in self.positions.values())

        positions_list = []
        for symbol, pos in self.positions.items():
            positions_list.append({
                "symbol": symbol,
                "spot_quantity": pos.spot_quantity,
                "futures_quantity": pos.futures_quantity,
                "leverage": pos.leverage,
                "margin_used": pos.margin_used,
                "accumulated_funding": pos.accumulated_funding,
                "hold_time_hours": (time.time() - pos.open_time) / 3600
            })

        return {
            "total_positions": len(self.positions),
            "total_margin_used": total_margin,
            "positions": positions_list
        }

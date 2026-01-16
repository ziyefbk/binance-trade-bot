"""
止损管理器
Agent 4 实现
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StopLossManager:
    """止损管理器"""

    def __init__(self, engine, config):
        """
        初始化止损管理器

        Args:
            engine: Rust BinanceEngine 实例
            config: RiskConfig 配置
        """
        self.engine = engine
        self.config = config
        self.stop_loss_percent = config.stop_loss_percent

        logger.info(f"止损管理器初始化: stop_loss={self.stop_loss_percent}%")

    def check_stop_loss(self, position) -> bool:
        """
        检查是否触发止损

        Args:
            position: Position 对象

        Returns:
            是否应该止损
        """
        if not position:
            return False

        # 计算当前亏损百分比
        loss_percent = -position.pnl_percent  # 负数表示亏损

        if loss_percent >= self.stop_loss_percent:
            logger.warning(f"触发止损: {position.symbol}, 亏损 {loss_percent:.2f}% >= "
                          f"{self.stop_loss_percent}%")
            return True

        return False

    def execute_stop_loss(self, position) -> dict:
        """
        执行止损

        Args:
            position: Position 对象

        Returns:
            {
                "success": bool,
                "symbol": str,
                "size": float,
                "price": float,
                "error": Optional[str]
            }
        """
        logger.warning(f"执行止损: {position.symbol}, size={position.size}")

        try:
            # 市价卖出止损
            result = self.engine.place_order(
                symbol=position.symbol,
                side="sell",
                quantity=position.size,
                order_type="market",
                price=None
            )

            if result.success:
                logger.info(f"止损成功: {position.symbol}, "
                          f"卖出 {result.executed_qty} @ ${result.avg_price:.2f}")

                return {
                    "success": True,
                    "symbol": position.symbol,
                    "size": result.executed_qty,
                    "price": result.avg_price,
                    "order_id": result.order_id,
                    "error": None
                }
            else:
                error_msg = result.error or "未知错误"
                logger.error(f"止损失败: {position.symbol}, {error_msg}")

                return {
                    "success": False,
                    "symbol": position.symbol,
                    "size": 0.0,
                    "price": 0.0,
                    "error": error_msg
                }

        except Exception as e:
            error_msg = f"止损执行异常: {str(e)}"
            logger.error(error_msg)

            return {
                "success": False,
                "symbol": position.symbol,
                "size": 0.0,
                "price": 0.0,
                "error": error_msg
            }

    def check_and_execute(self, position) -> Optional[dict]:
        """
        检查并执行止损（如果需要）

        Args:
            position: Position 对象

        Returns:
            如果执行了止损，返回执行结果；否则返回 None
        """
        if self.check_stop_loss(position):
            return self.execute_stop_loss(position)

        return None

    def monitor_all_positions(self, positions: dict) -> list:
        """
        监控所有持仓并执行止损

        Args:
            positions: 持仓字典 {symbol: Position}

        Returns:
            执行的止损结果列表
        """
        stop_loss_results = []

        for symbol, position in positions.items():
            result = self.check_and_execute(position)
            if result:
                stop_loss_results.append(result)

        if stop_loss_results:
            logger.warning(f"执行了 {len(stop_loss_results)} 个止损操作")

        return stop_loss_results

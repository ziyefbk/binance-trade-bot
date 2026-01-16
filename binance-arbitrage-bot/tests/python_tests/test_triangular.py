"""
三角套利策略单元测试
Agent 4 实现
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# 添加 python-strategy 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python-strategy'))

from strategies.triangular_arbitrage import TriangularArbitrage, TriangularPath
from risk_management.position_manager import PositionManager, Position
from risk_management.stop_loss import StopLossManager
from config import TriangularConfig, RiskConfig


class TestTriangularArbitrage:
    """测试三角套利策略"""

    def setup_method(self):
        """测试前准备"""
        # 创建 mock engine
        self.mock_engine = Mock()

        # 创建配置
        self.config = TriangularConfig(
            min_profit_percent=0.15,
            max_position_usdt=100.0,
            scan_interval_ms=100
        )

        # 创建策略实例
        self.strategy = TriangularArbitrage(self.mock_engine, self.config)

    def test_init(self):
        """测试初始化"""
        assert self.strategy.min_profit_threshold == 0.15
        assert self.strategy.max_position_size == 100.0
        assert self.strategy.scan_interval_ms == 100

    def test_parse_symbol(self):
        """测试交易对解析"""
        # 正常情况
        base, quote = self.strategy._parse_symbol("BTCUSDT")
        assert base == "BTC"
        assert quote == "USDT"

        base, quote = self.strategy._parse_symbol("ETHBTC")
        assert base == "ETH"
        assert quote == "BTC"

        # 边界情况
        base, quote = self.strategy._parse_symbol("BNBUSDT")
        assert base == "BNB"
        assert quote == "USDT"

    def test_generate_paths_empty(self):
        """测试空交易对列表"""
        paths = self.strategy.generate_paths([])
        assert len(paths) == 0

    def test_generate_paths_simple(self):
        """测试简单三角路径生成"""
        trading_pairs = ["BTCUSDT", "ETHBTC", "ETHUSDT"]
        paths = self.strategy.generate_paths(trading_pairs)

        # 应该至少能生成一些路径
        assert len(paths) > 0

        # 检查路径结构
        for path in paths:
            assert isinstance(path, TriangularPath)
            assert len(path.symbols) == 3
            assert path.base_asset
            assert path.intermediate_asset
            assert path.quote_asset

    def test_calculate_position_size(self):
        """测试仓位计算"""
        # 高利润机会
        high_profit_opp = {
            "profit_percent": 0.6,
            "estimated_amount": 200.0
        }
        size = self.strategy.calculate_position_size(high_profit_opp)
        assert size == 100.0  # 应该使用满仓

        # 中等利润机会
        medium_profit_opp = {
            "profit_percent": 0.4,
            "estimated_amount": 200.0
        }
        size = self.strategy.calculate_position_size(medium_profit_opp)
        assert size == 80.0  # 应该使用 80%

        # 低利润机会
        low_profit_opp = {
            "profit_percent": 0.2,
            "estimated_amount": 200.0
        }
        size = self.strategy.calculate_position_size(low_profit_opp)
        assert size == 50.0  # 应该使用 50%

    def test_scan_opportunities(self):
        """测试扫描套利机会"""
        # Mock 返回值
        mock_opp = Mock()
        mock_opp.path = ["BTCUSDT", "ETHBTC", "ETHUSDT"]
        mock_opp.profit_percent = 0.25
        mock_opp.estimated_amount = 100.0
        mock_opp.execution_prices = [50000.0, 0.05, 2500.0]
        mock_opp.timestamp = 1234567890

        self.mock_engine.get_arbitrage_opportunities.return_value = [mock_opp]

        opportunities = self.strategy.scan_opportunities()

        assert len(opportunities) == 1
        assert opportunities[0]["profit_percent"] == 0.25
        assert len(opportunities[0]["path"]) == 3

    def test_execute_success(self):
        """测试成功执行套利"""
        # Mock 执行结果
        mock_result = Mock()
        mock_result.profit_usdt = 15.0
        mock_result.profit_percent = 1.5
        mock_result.execution_time_ms = 150
        mock_result.initial_amount = 1000.0
        mock_result.final_amount = 1015.0

        self.mock_engine.execute_triangular_arbitrage.return_value = mock_result

        opportunity = {
            "path": ["BTCUSDT", "ETHBTC", "ETHUSDT"],
            "profit_percent": 0.5,
            "estimated_amount": 100.0
        }

        result = self.strategy.execute(opportunity)

        assert result["success"] is True
        assert result["profit_usdt"] == 15.0
        assert result["error"] is None


class TestPositionManager:
    """测试仓位管理器"""

    def setup_method(self):
        """测试前准备"""
        self.mock_engine = Mock()

        # 配置
        self.config = RiskConfig(
            max_total_position_percent=95.0,
            max_single_trade_percent=20.0,
            stop_loss_percent=2.0
        )

        self.manager = PositionManager(self.mock_engine, self.config)

    def test_init(self):
        """测试初始化"""
        assert self.manager.max_total_position_percent == 95.0
        assert self.manager.max_single_trade_percent == 20.0

    def test_get_total_balance_usdt_only_stable(self):
        """测试获取总资金 - 仅稳定币"""
        mock_balance = Mock()
        mock_balance.asset = "USDT"
        mock_balance.total = 1000.0

        self.mock_engine.get_balances.return_value = [mock_balance]

        total = self.manager.get_total_balance_usdt()
        assert total == 1000.0

    def test_can_open_position_sufficient_balance(self):
        """测试开仓检查 - 资金充足"""
        # Mock 总资金
        self.manager._total_balance_cache = 1000.0

        mock_balance = Mock()
        mock_balance.asset = "USDT"
        mock_balance.total = 1000.0
        mock_balance.locked = 0.0

        self.mock_engine.get_balances.return_value = [mock_balance]

        # 尝试开 100 USDT 的仓位 (10%)
        can_open = self.manager.can_open_position(100.0)
        assert can_open is True

    def test_can_open_position_insufficient_balance(self):
        """测试开仓检查 - 资金不足"""
        # Mock 总资金
        self.manager._total_balance_cache = 100.0

        mock_balance = Mock()
        mock_balance.asset = "USDT"
        mock_balance.total = 100.0
        mock_balance.locked = 0.0

        self.mock_engine.get_balances.return_value = [mock_balance]

        # 尝试开 500 USDT 的仓位
        can_open = self.manager.can_open_position(500.0)
        assert can_open is False

    def test_calculate_max_position_size(self):
        """测试最大仓位计算"""
        # Mock 总资金 1000 USDT
        self.manager._total_balance_cache = 1000.0

        mock_balance = Mock()
        mock_balance.asset = "USDT"
        mock_balance.total = 1000.0
        mock_balance.locked = 0.0

        self.mock_engine.get_balances.return_value = [mock_balance]

        max_size = self.manager.calculate_max_position_size("BTCUSDT")

        # max_single_trade_percent = 20%
        # 1000 * 20% = 200 USDT
        assert max_size == 200.0


class TestStopLossManager:
    """测试止损管理器"""

    def setup_method(self):
        """测试前准备"""
        self.mock_engine = Mock()

        self.config = RiskConfig(
            max_total_position_percent=95.0,
            max_single_trade_percent=20.0,
            stop_loss_percent=2.0
        )

        self.manager = StopLossManager(self.mock_engine, self.config)

    def test_init(self):
        """测试初始化"""
        assert self.manager.stop_loss_percent == 2.0

    def test_check_stop_loss_not_triggered(self):
        """测试止损检查 - 未触发"""
        position = Position(
            symbol="BTCUSDT",
            size=0.1,
            entry_price=50000.0,
            current_price=50500.0,
            unrealized_pnl=50.0  # 盈利
        )

        should_stop = self.manager.check_stop_loss(position)
        assert should_stop is False

    def test_check_stop_loss_triggered(self):
        """测试止损检查 - 已触发"""
        position = Position(
            symbol="BTCUSDT",
            size=0.1,
            entry_price=50000.0,
            current_price=49000.0,
            unrealized_pnl=-100.0  # 亏损 2%
        )

        # 修改 unrealized_pnl 使其触发止损
        position.unrealized_pnl = -100.0
        # 需要亏损达到 2% 即 50000 * 0.1 * 0.02 = 100 USDT

        should_stop = self.manager.check_stop_loss(position)
        assert should_stop is True

    def test_execute_stop_loss_success(self):
        """测试执行止损 - 成功"""
        position = Position(
            symbol="BTCUSDT",
            size=0.1,
            entry_price=50000.0,
            current_price=49000.0,
            unrealized_pnl=-100.0
        )

        # Mock 执行结果
        mock_result = Mock()
        mock_result.success = True
        mock_result.executed_qty = 0.1
        mock_result.avg_price = 49000.0
        mock_result.order_id = 12345

        self.mock_engine.place_order.return_value = mock_result

        result = self.manager.execute_stop_loss(position)

        assert result["success"] is True
        assert result["symbol"] == "BTCUSDT"
        assert result["size"] == 0.1
        assert result["error"] is None


def test_position_pnl_percent():
    """测试持仓盈亏百分比计算"""
    position = Position(
        symbol="BTCUSDT",
        size=0.1,
        entry_price=50000.0,
        current_price=51000.0,
        unrealized_pnl=100.0
    )

    # PNL% = 100 / (0.1 * 50000) * 100 = 2%
    assert abs(position.pnl_percent - 2.0) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=strategies", "--cov=risk_management"])

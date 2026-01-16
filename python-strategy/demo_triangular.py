"""
三角套利策略演示脚本
展示如何使用 Agent 4 实现的模块
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_with_mock_engine():
    """使用 Mock 引擎演示(不需要真实的 Rust 引擎)"""
    from unittest.mock import Mock
    from config import TriangularConfig, RiskConfig
    from strategies.triangular_arbitrage import TriangularArbitrage
    from risk_management.position_manager import PositionManager
    from risk_management.stop_loss import StopLossManager

    logger.info("=" * 60)
    logger.info("三角套利策略演示 (Mock 模式)")
    logger.info("=" * 60)

    # 1. 创建 Mock 引擎
    mock_engine = Mock()
    logger.info("✓ 创建 Mock 引擎")

    # 2. 创建配置
    triangular_config = TriangularConfig(
        min_profit_percent=0.15,
        max_position_usdt=100.0,
        scan_interval_ms=100
    )
    logger.info("✓ 创建三角套利配置")

    risk_config = RiskConfig(
        max_total_position_percent=95.0,
        max_single_trade_percent=20.0,
        stop_loss_percent=2.0
    )
    logger.info("✓ 创建风险管理配置")

    # 3. 初始化策略
    strategy = TriangularArbitrage(mock_engine, triangular_config)
    logger.info("✓ 初始化三角套利策略")

    # 4. 生成套利路径
    trading_pairs = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT",
        "ETHBTC", "BNBBTC", "BNBETH"
    ]
    logger.info(f"\n使用交易对: {trading_pairs}")

    paths = strategy.generate_paths(trading_pairs)
    logger.info(f"\n✓ 生成了 {len(paths)} 条三角套利路径")

    if paths:
        logger.info("\n前 5 条路径示例:")
        for i, path in enumerate(paths[:5], 1):
            logger.info(f"  {i}. {path}")

    # 5. 演示仓位管理
    logger.info("\n" + "=" * 60)
    logger.info("仓位管理演示")
    logger.info("=" * 60)

    position_manager = PositionManager(mock_engine, risk_config)

    # Mock 余额
    mock_balance = Mock()
    mock_balance.asset = "USDT"
    mock_balance.total = 1000.0
    mock_balance.free = 1000.0
    mock_balance.locked = 0.0
    mock_engine.get_balances.return_value = [mock_balance]

    total_balance = position_manager.get_total_balance_usdt()
    logger.info(f"✓ 总资金: ${total_balance:.2f} USDT")

    available = position_manager.get_available_balance()
    logger.info(f"✓ 可用资金: ${available:.2f} USDT")

    max_position = position_manager.calculate_max_position_size("BTCUSDT")
    logger.info(f"✓ 最大单笔仓位: ${max_position:.2f} USDT")

    can_open_100 = position_manager.can_open_position(100.0)
    logger.info(f"✓ 能否开 $100 USDT 仓位: {'是' if can_open_100 else '否'}")

    can_open_500 = position_manager.can_open_position(500.0)
    logger.info(f"✓ 能否开 $500 USDT 仓位: {'是' if can_open_500 else '否'}")

    # 6. 演示仓位计算
    logger.info("\n" + "=" * 60)
    logger.info("动态仓位计算演示")
    logger.info("=" * 60)

    opportunities = [
        {"profit_percent": 0.6, "estimated_amount": 200.0, "name": "高利润机会"},
        {"profit_percent": 0.4, "estimated_amount": 200.0, "name": "中等利润机会"},
        {"profit_percent": 0.2, "estimated_amount": 200.0, "name": "低利润机会"},
    ]

    for opp in opportunities:
        size = strategy.calculate_position_size(opp)
        logger.info(f"{opp['name']} (利润 {opp['profit_percent']}%): "
                   f"建议仓位 ${size:.2f} USDT")

    # 7. 演示止损管理
    logger.info("\n" + "=" * 60)
    logger.info("止损管理演示")
    logger.info("=" * 60)

    from risk_management.position_manager import Position

    stop_loss_manager = StopLossManager(mock_engine, risk_config)

    # 创建测试持仓
    profitable_position = Position(
        symbol="BTCUSDT",
        size=0.1,
        entry_price=50000.0,
        current_price=51000.0,
        unrealized_pnl=100.0
    )

    loss_position = Position(
        symbol="ETHUSDT",
        size=1.0,
        entry_price=2500.0,
        current_price=2450.0,
        unrealized_pnl=-50.0
    )

    should_stop_profit = stop_loss_manager.check_stop_loss(profitable_position)
    logger.info(f"✓ 盈利持仓需要止损: {'是' if should_stop_profit else '否'}")

    should_stop_loss = stop_loss_manager.check_stop_loss(loss_position)
    logger.info(f"✓ 亏损持仓需要止损: {'是' if should_stop_loss else '否'}")

    logger.info("\n" + "=" * 60)
    logger.info("演示完成!")
    logger.info("=" * 60)
    logger.info("\n提示: 要使用真实的 Rust 引擎,请参考 main.py")


def demo_with_real_engine():
    """使用真实的 Rust 引擎演示(需要 API 密钥)"""
    logger.info("\n要使用真实引擎,请:")
    logger.info("1. 在 config/config.yaml 中配置 API 密钥")
    logger.info("2. 编译 Rust 模块: cd rust-core && maturin develop")
    logger.info("3. 运行: python python-strategy/main.py --testnet")


if __name__ == "__main__":
    try:
        demo_with_mock_engine()
        print()
        demo_with_real_engine()

    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
    except Exception as e:
        logger.error(f"发生错误: {e}", exc_info=True)

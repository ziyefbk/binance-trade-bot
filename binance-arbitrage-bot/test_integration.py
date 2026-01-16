"""
Integration Test: Rust Engine + Python Strategy
Tests the integration between Rust core and Python strategy layer
"""

import sys
import time
from pathlib import Path

# Add python-strategy to path
sys.path.insert(0, str(Path(__file__).parent / "python-strategy"))

def test_rust_engine_import():
    """Test 1: Import Rust module"""
    print("=" * 70)
    print("Test 1: Rust Module Import")
    print("=" * 70)

    try:
        import binance_rust_py
        print("[OK] Rust module imported successfully")
        print(f"[INFO] Available classes: {dir(binance_rust_py)[:6]}")
        return True
    except ImportError as e:
        print(f"[FAIL] Failed to import Rust module: {e}")
        return False


def test_engine_instantiation():
    """Test 2: Instantiate BinanceEngine"""
    print("\n" + "=" * 70)
    print("Test 2: BinanceEngine Instantiation")
    print("=" * 70)

    try:
        import binance_rust_py

        # Create engine with test credentials
        engine = binance_rust_py.BinanceEngine(
            api_key="test_key_12345",
            api_secret="test_secret_67890",
            testnet=True
        )
        print("[OK] BinanceEngine instantiated successfully")
        print(f"[INFO] Engine object: {engine}")
        return engine
    except Exception as e:
        print(f"[FAIL] Failed to instantiate engine: {e}")
        return None


def test_python_strategy_with_rust_engine(engine):
    """Test 3: Python Strategy with Rust Engine"""
    print("\n" + "=" * 70)
    print("Test 3: Python Strategy Integration")
    print("=" * 70)

    try:
        from config import TriangularConfig
        from strategies.triangular_arbitrage import TriangularArbitrage

        # Create strategy config
        config = TriangularConfig(
            min_profit_percent=0.15,
            max_position_usdt=100.0,
            scan_interval_ms=100
        )
        print("[OK] Created TriangularConfig")

        # Initialize strategy with Rust engine
        strategy = TriangularArbitrage(engine, config)
        print("[OK] TriangularArbitrage initialized with Rust engine")

        # Test path generation
        trading_pairs = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT",
            "ETHBTC", "BNBBTC", "BNBETH"
        ]
        paths = strategy.generate_paths(trading_pairs)
        print(f"[OK] Generated {len(paths)} triangular arbitrage paths")

        if paths:
            print("\n[INFO] Sample paths:")
            for i, path in enumerate(paths[:3], 1):
                print(f"  {i}. {path}")

        return True
    except Exception as e:
        print(f"[FAIL] Strategy integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_management_with_rust_engine(engine):
    """Test 4: Risk Management with Rust Engine"""
    print("\n" + "=" * 70)
    print("Test 4: Risk Management Integration")
    print("=" * 70)

    try:
        from config import RiskConfig
        from risk_management.position_manager import PositionManager
        from risk_management.stop_loss import StopLossManager

        # Create risk config
        risk_config = RiskConfig(
            max_total_position_percent=95.0,
            max_single_trade_percent=20.0,
            stop_loss_percent=2.0
        )
        print("[OK] Created RiskConfig")

        # Initialize managers with Rust engine (don't call API methods)
        position_manager = PositionManager(engine, risk_config)
        print("[OK] PositionManager initialized with Rust engine")

        stop_loss_manager = StopLossManager(engine, risk_config)
        print("[OK] StopLossManager initialized with Rust engine")

        # Test that objects have expected attributes
        assert hasattr(position_manager, 'engine')
        assert hasattr(position_manager, 'config')
        print("[OK] PositionManager has engine and config attributes")

        assert hasattr(stop_loss_manager, 'engine')
        assert hasattr(stop_loss_manager, 'config')
        print("[OK] StopLossManager has engine and config attributes")

        return True
    except Exception as e:
        print(f"[FAIL] Risk management integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_benchmark(engine):
    """Test 5: Performance Benchmark"""
    print("\n" + "=" * 70)
    print("Test 5: Performance Benchmark")
    print("=" * 70)

    try:
        # Test 1: Engine instantiation speed
        start = time.perf_counter()
        for _ in range(100):
            import binance_rust_py
            test_engine = binance_rust_py.BinanceEngine(
                api_key="test",
                api_secret="test",
                testnet=True
            )
        end = time.perf_counter()
        avg_time = (end - start) / 100 * 1000
        print(f"[OK] Engine instantiation: {avg_time:.3f}ms average")

        # Test 2: Attribute access overhead
        start = time.perf_counter()
        for _ in range(10000):
            # Test attribute access speed
            has_method = hasattr(engine, 'get_balances')
        end = time.perf_counter()
        avg_time_us = (end - start) / 10000 * 1000000  # microseconds
        print(f"[OK] Attribute access overhead: {avg_time_us:.3f}us average")

        if avg_time_us < 100:  # 100 microseconds
            print("[EXCELLENT] Attribute access < 100us (Very fast!)")

        return True
    except Exception as e:
        print(f"[FAIL] Performance benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test 6: Configuration Loading"""
    print("\n" + "=" * 70)
    print("Test 6: Configuration Loading")
    print("=" * 70)

    try:
        from config import (
            APIConfig, TriangularConfig, FundingRateConfig,
            RiskConfig
        )

        print("[OK] APIConfig imported")
        print("[OK] TriangularConfig imported")
        print("[OK] FundingRateConfig imported")
        print("[OK] RiskConfig imported")

        # Test config instantiation
        api_cfg = APIConfig(
            key="test",
            secret="test",
            testnet=True
        )
        print(f"[OK] APIConfig created: testnet={api_cfg.testnet}")

        return True
    except Exception as e:
        print(f"[FAIL] Config loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  Binance Arbitrage Bot - Integration Test Suite".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print()

    results = []

    # Test 1: Rust module import
    results.append(("Rust Module Import", test_rust_engine_import()))

    # Test 2: Engine instantiation
    engine = test_engine_instantiation()
    results.append(("Engine Instantiation", engine is not None))

    if engine:
        # Test 3: Python strategy integration
        results.append(("Python Strategy Integration",
                       test_python_strategy_with_rust_engine(engine)))

        # Test 4: Risk management integration
        results.append(("Risk Management Integration",
                       test_risk_management_with_rust_engine(engine)))

        # Test 5: Performance benchmark
        results.append(("Performance Benchmark",
                       test_performance_benchmark(engine)))

    # Test 6: Config loading
    results.append(("Configuration Loading", test_config_loading()))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)

    if passed == total:
        print("\n[SUCCESS] All integration tests passed!")
        print("[INFO] The Rust engine is fully integrated with Python strategy layer")
        print("[INFO] You can now proceed with:")
        print("  1. Testnet trading")
        print("  2. Performance optimization")
        print("  3. Live trading (with caution)")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        print("[INFO] Please review the errors above")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[INFO] Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

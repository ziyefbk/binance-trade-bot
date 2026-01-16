"""
Testnet Validation Script
Tests API connectivity and basic trading functionality on Binance Testnet

Usage:
    python test_testnet.py                    # Basic tests (no API key)
    python test_testnet.py --with-api         # Full tests (requires API key in config)
"""

import sys
import time
import argparse
from pathlib import Path

# Add python-strategy to path
sys.path.insert(0, str(Path(__file__).parent / "python-strategy"))


def test_rust_engine_connectivity():
    """Test 1: Basic Rust engine instantiation with testnet mode"""
    print("=" * 70)
    print("Test 1: Rust Engine Connectivity (Testnet Mode)")
    print("=" * 70)

    try:
        import binance_rust_py

        # Create engine with dummy credentials (just to test instantiation)
        engine = binance_rust_py.BinanceEngine(
            api_key="test_api_key",
            api_secret="test_api_secret",
            testnet=True
        )
        print("[OK] BinanceEngine instantiated in testnet mode")
        print(f"[OK] Engine object: {engine}")
        return engine

    except Exception as e:
        print(f"[FAIL] Failed to instantiate engine: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_config_loading():
    """Test 2: Load configuration from config.yaml"""
    print("\n" + "=" * 70)
    print("Test 2: Configuration Loading")
    print("=" * 70)

    try:
        import yaml

        config_path = Path(__file__).parent / "binance-arbitrage-bot" / "config" / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print("[OK] Config file loaded successfully")
        print(f"[INFO] Testnet mode: {config['api']['testnet']}")
        print(f"[INFO] Strategy mode: {config['strategy']['mode']}")
        print(f"[INFO] Trading pairs: {len(config['trading_pairs'])} pairs")

        # Check if API keys are set
        api_key = config['api']['key']
        api_secret = config['api']['secret']

        if api_key == "your_api_key_here" or api_secret == "your_api_secret_here":
            print("\n[WARNING] API keys not configured in config.yaml")
            print("[INFO] Using placeholder keys for basic tests")
            return config, False
        else:
            print("[OK] API keys configured")
            return config, True

    except Exception as e:
        print(f"[FAIL] Failed to load config: {e}")
        import traceback
        traceback.print_exc()
        return None, False


def test_strategy_initialization(engine, config):
    """Test 3: Initialize strategy with Rust engine"""
    print("\n" + "=" * 70)
    print("Test 3: Strategy Initialization")
    print("=" * 70)

    try:
        from config import TriangularConfig
        from strategies.triangular_arbitrage import TriangularArbitrage

        # Create strategy config from YAML
        strategy_config = TriangularConfig(
            min_profit_percent=config['strategy']['triangular']['min_profit_percent'],
            max_position_usdt=config['strategy']['triangular']['max_position_usdt'],
            scan_interval_ms=config['strategy']['triangular']['scan_interval_ms']
        )
        print("[OK] TriangularConfig created from config.yaml")

        # Initialize strategy
        strategy = TriangularArbitrage(engine, strategy_config)
        print("[OK] TriangularArbitrage strategy initialized")

        # Generate paths from config trading pairs
        trading_pairs = config['trading_pairs']
        print(f"[INFO] Using {len(trading_pairs)} trading pairs from config")

        paths = strategy.generate_paths(trading_pairs)
        print(f"[OK] Generated {len(paths)} arbitrage paths")

        if paths:
            print("\n[INFO] Sample paths (first 5):")
            for i, path in enumerate(paths[:5], 1):
                print(f"  {i}. {path}")

        return strategy

    except Exception as e:
        print(f"[FAIL] Strategy initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_api_connection(engine):
    """Test 4: Test actual API connection (requires valid API keys)"""
    print("\n" + "=" * 70)
    print("Test 4: API Connection Test")
    print("=" * 70)

    try:
        print("[INFO] Attempting to connect to Binance Testnet API...")

        # Try to get account information
        account_info = engine.get_account_info()
        print("[OK] Successfully connected to Binance Testnet!")
        print(f"[OK] Account info retrieved: {account_info}")

        # Get balances
        balances = engine.get_balances()
        print(f"[OK] Retrieved {len(balances)} asset balances")

        # Show non-zero balances
        non_zero = [b for b in balances if b.free > 0 or b.locked > 0]
        if non_zero:
            print("\n[INFO] Non-zero balances:")
            for balance in non_zero[:10]:  # Show first 10
                print(f"  {balance.asset}: {balance.free:.8f} (free), {balance.locked:.8f} (locked)")
        else:
            print("\n[WARNING] No non-zero balances found")
            print("[INFO] You may need to fund your testnet account")
            print("[INFO] Get testnet funds at: https://testnet.binance.vision/")

        return True

    except Exception as e:
        print(f"[FAIL] API connection failed: {e}")
        print("\n[INFO] Possible reasons:")
        print("  1. Invalid API keys")
        print("  2. Network connectivity issues")
        print("  3. API keys not configured for testnet")
        print("\n[INFO] To get testnet API keys:")
        print("  1. Visit https://testnet.binance.vision/")
        print("  2. Login with GitHub")
        print("  3. Generate API key and secret")
        print("  4. Update config/config.yaml with your keys")
        import traceback
        traceback.print_exc()
        return False


def test_market_data(engine):
    """Test 5: Test market data retrieval"""
    print("\n" + "=" * 70)
    print("Test 5: Market Data Retrieval")
    print("=" * 70)

    try:
        # Test getting ticker price
        symbol = "BTCUSDT"
        print(f"[INFO] Fetching ticker price for {symbol}...")

        # Note: This will fail if API methods aren't implemented
        # For now, we'll skip this test
        print("[SKIP] Market data test requires full API implementation")
        print("[INFO] This will be tested in the actual trading flow")

        return True

    except Exception as e:
        print(f"[FAIL] Market data retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_metrics(engine):
    """Test 6: Performance benchmarking on testnet"""
    print("\n" + "=" * 70)
    print("Test 6: Performance Benchmarking")
    print("=" * 70)

    try:
        import binance_rust_py

        # Benchmark 1: Engine creation speed
        print("[INFO] Benchmarking engine instantiation...")
        start = time.perf_counter()
        for _ in range(100):
            test_engine = binance_rust_py.BinanceEngine(
                api_key="test",
                api_secret="test",
                testnet=True
            )
        end = time.perf_counter()
        avg_ms = (end - start) / 100 * 1000
        print(f"[OK] Engine instantiation: {avg_ms:.3f}ms average (100 iterations)")

        # Benchmark 2: Attribute access
        print("[INFO] Benchmarking attribute access...")
        start = time.perf_counter()
        for _ in range(10000):
            _ = hasattr(engine, 'get_balances')
        end = time.perf_counter()
        avg_us = (end - start) / 10000 * 1000000
        print(f"[OK] Attribute access: {avg_us:.3f}us average (10000 iterations)")

        if avg_us < 100:
            print("[EXCELLENT] Attribute access < 100us")

        return True

    except Exception as e:
        print(f"[FAIL] Performance benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Binance Testnet Validation')
    parser.add_argument('--with-api', action='store_true',
                       help='Run tests that require API keys')
    args = parser.parse_args()

    print("\n" + "*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  Binance Arbitrage Bot - Testnet Validation".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print()

    results = []

    # Test 1: Engine connectivity
    engine = test_rust_engine_connectivity()
    results.append(("Engine Connectivity", engine is not None))

    if not engine:
        print("\n[FATAL] Cannot proceed without engine")
        return 1

    # Test 2: Config loading
    config, has_api_keys = test_config_loading()
    results.append(("Configuration Loading", config is not None))

    if not config:
        print("\n[FATAL] Cannot proceed without config")
        return 1

    # Test 3: Strategy initialization
    strategy = test_strategy_initialization(engine, config)
    results.append(("Strategy Initialization", strategy is not None))

    # Test 4: API connection (only if keys provided)
    if args.with_api:
        if has_api_keys:
            api_connected = test_api_connection(engine)
            results.append(("API Connection", api_connected))
        else:
            print("\n" + "=" * 70)
            print("Test 4: API Connection Test")
            print("=" * 70)
            print("[SKIP] API keys not configured in config.yaml")
            print("[INFO] Configure keys to run API tests")
            results.append(("API Connection", None))  # None = skipped

    # Test 5: Market data (skipped for now)
    # results.append(("Market Data", test_market_data(engine)))

    # Test 6: Performance
    perf_result = test_performance_metrics(engine)
    results.append(("Performance Benchmark", perf_result))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)

    for test_name, result in results:
        if result is True:
            status = "[PASS]"
        elif result is False:
            status = "[FAIL]"
        else:
            status = "[SKIP]"
        print(f"{status} {test_name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} passed, {failed}/{total} failed, {skipped}/{total} skipped")
    print("=" * 70)

    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
        if not args.with_api:
            print("\n[INFO] Run with --with-api flag to test API connectivity")
            print("[INFO] Example: python test_testnet.py --with-api")
        else:
            print("\n[INFO] Testnet validation complete!")
            print("[INFO] You can now proceed with:")
            print("  1. Backtest mode: python python-strategy/main.py --backtest")
            print("  2. Live testnet: python python-strategy/main.py --testnet")
        return 0
    else:
        print(f"\n[WARNING] {failed} test(s) failed")
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

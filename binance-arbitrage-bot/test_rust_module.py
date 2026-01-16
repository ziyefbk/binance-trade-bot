"""
Test script for verifying Rust module functionality
"""
import sys

def test_rust_module():
    """Test basic Rust module functionality"""
    print("=" * 60)
    print("Testing Rust Module (binance_rust_py)")
    print("=" * 60)

    try:
        import binance_rust_py
        print("[OK] Module imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import module: {e}")
        return False

    # Test BinanceEngine class availability
    try:
        engine_class = binance_rust_py.BinanceEngine
        print(f"[OK] BinanceEngine class available: {engine_class}")
    except AttributeError as e:
        print(f"[FAIL] BinanceEngine not found: {e}")
        return False

    # Test other classes
    classes = [
        'PyAccountInfo',
        'PyArbitrageOpportunity',
        'PyArbitrageResult',
        'PyBalance',
        'PyExecutionResult'
    ]

    for cls_name in classes:
        try:
            cls = getattr(binance_rust_py, cls_name)
            print(f"[OK] {cls_name} class available")
        except AttributeError as e:
            print(f"[FAIL] {cls_name} not found: {e}")
            return False

    # Test BinanceEngine instantiation (will need API keys in real usage)
    print("\n" + "=" * 60)
    print("Testing BinanceEngine Instantiation")
    print("=" * 60)

    try:
        # Create engine with dummy credentials (testnet mode)
        engine = binance_rust_py.BinanceEngine(
            api_key="test_api_key",
            api_secret="test_api_secret",
            testnet=True
        )
        print("[OK] BinanceEngine instantiated successfully")
        print(f"     Engine object: {engine}")

        # Test available methods
        methods = [
            'start_market_data',
            'stop_market_data',
            'get_account_info',
            'get_price',
            'get_arbitrage_opportunities',
            'execute_triangular_arbitrage',
            'place_order',
            'cancel_order',
            'get_balances',
            'get_ticker_price'
        ]

        print("\n[INFO] Available methods:")
        for method in methods:
            if hasattr(engine, method):
                print(f"  [OK] {method}")
            else:
                print(f"  [WARN] {method} not found")

    except Exception as e:
        print(f"[FAIL] Failed to instantiate BinanceEngine: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nRust module is ready for use.")
    print("Note: Actual trading requires valid API keys in config.yaml")

    return True

if __name__ == "__main__":
    success = test_rust_module()
    sys.exit(0 if success else 1)

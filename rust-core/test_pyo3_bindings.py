#!/usr/bin/env python3
"""
PyO3 绑定层测试脚本
测试 binance_rust_py 模块的基本功能

使用方法:
    maturin develop  # 先编译安装模块
    python test_pyo3_bindings.py
"""

def test_import():
    """测试导入模块"""
    print("=" * 60)
    print("测试 1: 导入模块")
    print("=" * 60)

    try:
        import binance_rust_py
        print("✅ 成功导入 binance_rust_py 模块")

        # 检查所有类是否存在
        classes = [
            'BinanceEngine',
            'PyArbitrageOpportunity',
            'PyArbitrageResult',
            'PyExecutionResult',
            'PyBalance',
            'PyAccountInfo'
        ]

        for cls in classes:
            assert hasattr(binance_rust_py, cls), f"缺少类: {cls}"
            print(f"  ✓ {cls} 类存在")

        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_engine_creation():
    """测试创建 BinanceEngine"""
    print("\n" + "=" * 60)
    print("测试 2: 创建 BinanceEngine 实例")
    print("=" * 60)

    try:
        from binance_rust_py import BinanceEngine

        # 使用测试凭证创建引擎
        engine = BinanceEngine(
            api_key="test_api_key",
            api_secret="test_api_secret",
            testnet=True
        )

        print("✅ 成功创建 BinanceEngine 实例")
        print(f"  类型: {type(engine)}")

        return engine
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_data_classes():
    """测试数据类的字符串表示"""
    print("\n" + "=" * 60)
    print("测试 3: 数据类字符串表示")
    print("=" * 60)

    try:
        from binance_rust_py import PyBalance, PyAccountInfo

        # 创建测试余额
        balance = PyBalance()
        balance.asset = "BTC"
        balance.free = 1.5
        balance.locked = 0.5

        print("✅ PyBalance:")
        print(f"  repr: {repr(balance)}")
        print(f"  str: {str(balance)}")
        print(f"  total: {balance.total}")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_method_calls(engine):
    """测试方法调用"""
    print("\n" + "=" * 60)
    print("测试 4: 方法调用")
    print("=" * 60)

    if engine is None:
        print("⚠️  跳过测试（引擎未创建）")
        return False

    try:
        # 测试 get_price (应该返回 0.0，因为没有数据)
        price = engine.get_price("BTCUSDT")
        print(f"✅ get_price('BTCUSDT'): {price}")

        # 测试 get_arbitrage_opportunities (应该返回空列表)
        opportunities = engine.get_arbitrage_opportunities(0.15)
        print(f"✅ get_arbitrage_opportunities(0.15): {len(opportunities)} 个机会")

        return True
    except Exception as e:
        print(f"❌ 方法调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling(engine):
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 5: 错误处理")
    print("=" * 60)

    if engine is None:
        print("⚠️  跳过测试（引擎未创建）")
        return False

    try:
        # 测试无效的订单方向
        try:
            result = engine.place_order(
                symbol="BTCUSDT",
                side="invalid_side",  # 错误的方向
                quantity=0.1,
                order_type="market",
                price=None
            )
            print("❌ 应该抛出 ValueError")
            return False
        except ValueError as e:
            print(f"✅ 正确捕获 ValueError: {e}")

        # 测试限价单缺少价格参数
        try:
            result = engine.place_order(
                symbol="BTCUSDT",
                side="buy",
                quantity=0.1,
                order_type="limit",
                price=None  # 限价单需要价格
            )
            print("❌ 应该抛出 ValueError")
            return False
        except ValueError as e:
            print(f"✅ 正确捕获 ValueError: {e}")

        return True
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_type_hints():
    """测试类型提示"""
    print("\n" + "=" * 60)
    print("测试 6: 类型提示文件")
    print("=" * 60)

    try:
        import binance_rust_py

        # 检查是否有 __file__ 属性
        if hasattr(binance_rust_py, '__file__'):
            module_path = binance_rust_py.__file__
            print(f"  模块路径: {module_path}")

            # 检查 .pyi 文件
            import os
            pyi_path = module_path.replace('.pyd', '.pyi').replace('.so', '.pyi')
            if os.path.exists(pyi_path):
                print(f"✅ 找到类型提示文件: {pyi_path}")
            else:
                print(f"⚠️  类型提示文件不存在: {pyi_path}")
                print("  (这是正常的，.pyi 文件在 rust-core 目录)")

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("PyO3 绑定层测试")
    print("Agent 3 - binance_rust_py 模块")
    print("=" * 60)

    results = []

    # 1. 测试导入
    results.append(("导入模块", test_import()))

    # 2. 测试创建引擎
    engine = test_engine_creation()
    results.append(("创建引擎", engine is not None))

    # 3. 测试数据类
    results.append(("数据类", test_data_classes()))

    # 4. 测试方法调用
    results.append(("方法调用", test_method_calls(engine)))

    # 5. 测试错误处理
    results.append(("错误处理", test_error_handling(engine)))

    # 6. 测试类型提示
    results.append(("类型提示", test_type_hints()))

    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("-" * 60)
    print(f"总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！PyO3 绑定层工作正常！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

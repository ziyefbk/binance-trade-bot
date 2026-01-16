"""
币安套利机器人 - Python 纯测试版
用于在没有 Rust 模块的情况下测试 Python 策略逻辑
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试关键模块是否可以导入"""
    print("=" * 60)
    print("测试 Python 环境和依赖")
    print("=" * 60)

    try:
        import yaml
        print("[OK] PyYAML:", yaml.__version__)
    except ImportError as e:
        print("[FAIL] PyYAML:", e)

    try:
        import pandas as pd
        print("[OK] Pandas:", pd.__version__)
    except ImportError as e:
        print("[FAIL] Pandas:", e)

    try:
        import numpy as np
        print("[OK] NumPy:", np.__version__)
    except ImportError as e:
        print("[FAIL] NumPy:", e)

    try:
        from rich import print as rprint
        print("[OK] Rich: Available")
    except ImportError as e:
        print("[FAIL] Rich:", e)

    try:
        import matplotlib
        print("[OK] Matplotlib:", matplotlib.__version__)
    except ImportError as e:
        print("[FAIL] Matplotlib:", e)

    try:
        import plotly
        print("[OK] Plotly:", plotly.__version__)
    except ImportError as e:
        print("[FAIL] Plotly:", e)

    print("\n" + "=" * 60)
    print("测试项目结构")
    print("=" * 60)

    # Check project structure
    project_root = Path(__file__).parent

    dirs_to_check = [
        "strategies",
        "risk_management",
        "monitor",
        "backtest",
        "utils"
    ]

    for dir_name in dirs_to_check:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"[OK] {dir_name}/ directory exists")
            # Count Python files
            py_files = list(dir_path.glob("*.py"))
            print(f"  -> {len(py_files)} Python files")
        else:
            print(f"[FAIL] {dir_name}/ directory not found")

    print("\n" + "=" * 60)
    print("测试策略模块导入")
    print("=" * 60)

    try:
        from strategies import triangular_arbitrage
        print("[OK] Triangular arbitrage strategy module")
    except ImportError as e:
        print(f"[FAIL] Triangular arbitrage strategy module: {e}")

    try:
        from strategies import funding_rate
        print("[OK] Funding rate arbitrage strategy module")
    except ImportError as e:
        print(f"[FAIL] Funding rate arbitrage strategy module: {e}")

    try:
        from risk_management import position_manager
        print("[OK] Position manager module")
    except ImportError as e:
        print(f"[FAIL] Position manager module: {e}")

    try:
        from risk_management import stop_loss
        print("[OK] Stop loss module")
    except ImportError as e:
        print(f"[FAIL] Stop loss module: {e}")

    print("\n" + "=" * 60)
    print("测试配置文件")
    print("=" * 60)

    config_path = project_root.parent / "config" / "config.yaml"
    if config_path.exists():
        print(f"[OK] Config file exists: {config_path}")
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f"  -> Config loaded successfully")
            if 'binance' in config:
                print(f"  -> Contains binance config")
            if 'strategy' in config:
                print(f"  -> Contains strategy config")
        except Exception as e:
            print(f"  [FAIL] Config file parse error: {e}")
    else:
        print(f"[FAIL] Config file not found: {config_path}")

    print("\n" + "=" * 60)
    print("Environment test complete!")
    print("=" * 60)
    print("\nNote: Rust core module needs separate compilation")
    print("Run the following command to compile Rust module:")
    print("  cd ../rust-core")
    print("  maturin develop --release")
    print("\nOr use Docker for full deployment")

if __name__ == "__main__":
    test_imports()

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a **币安套利交易机器人** (Binance Arbitrage Bot) - a high-performance, low-latency trading system that implements two core arbitrage strategies:

1. **三角套利** (Triangular Arbitrage) - Exploits price inefficiencies across three trading pairs
2. **资金费率套利** (Funding Rate Arbitrage) - Profits from spot-futures funding rate differentials

## Architecture

The project uses a **hybrid Rust + Python architecture** for optimal performance and flexibility:

### Core Components

```
binance-arbitrage-bot/
├── rust-core/              # High-performance trading engine (Rust)
│   ├── binance/           # Binance API client (REST + WebSocket)
│   ├── engine/            # Order executor, price monitor, rate limiter
│   └── utils/             # Calculation utilities
│
├── python-strategy/        # Strategy and risk management layer (Python)
│   ├── strategies/        # Arbitrage strategies (triangular, funding rate, hybrid)
│   ├── risk_management/   # Position manager, stop-loss
│   ├── monitor/           # Real-time dashboard and logging
│   ├── backtest/          # Backtesting engine and visualization
│   └── utils/             # Leverage calculator, liquidation monitor
│
├── config/                # YAML configuration files
├── docs/                  # Documentation and specifications
└── tests/                 # Unit tests (Python + Rust)
```

### Technology Stack

- **Rust**: 1.75+ (async runtime with Tokio, WebSocket with tungstenite, PyO3 bindings)
- **Python**: 3.7+ (推荐 3.11)
- **Key Libraries**:
  - Rust: tokio, reqwest, pyo3, dashmap, serde
  - Python: pandas, numpy, rich, matplotlib, plotly, backtrader

## Build and Development Commands

### 1. Initial Setup

```bash
# Clone and enter project directory
cd binance-arbitrage-bot

# Install Rust (if not installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Maturin (PyO3 build tool)
pip install maturin
```

### 2. Build Rust Core

**✅ STATUS: COMPLETED** - Rust module已成功编译并安装

```bash
cd rust-core
# Build production wheel
maturin build --release --interpreter D:/Anaconda3/envs/math/python.exe

# Install the wheel
pip install target/wheels/binance_rust_py-0.1.0-cp37-abi3-win_amd64.whl

# Verify installation
python -c "import binance_rust_py; print('Rust module loaded successfully!')"
cd ..
```

**详细信息**: 参见 [RUST_MODULE_STATUS.md](binance-arbitrage-bot/RUST_MODULE_STATUS.md)

### 3. Install Python Dependencies

```bash
cd python-strategy
pip install -r requirements.txt
cd ..
```

### 4. Configure API Keys

```bash
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your Binance API credentials
```

### 5. Run the Bot

```bash
cd python-strategy

# Backtest mode (no API required)
python main.py --backtest

# Paper trading on testnet
python main.py --testnet

# Live trading (use with caution!)
python main.py --live
```

## Testing Strategy

### Run Python Tests
```bash
cd tests/python_tests
pytest test_triangular.py -v --cov
```

### Run Rust Tests
```bash
cd rust-core
cargo test
```

### Integration Testing
```bash
# Test PyO3 bindings
cd python-strategy
python demo_triangular.py    # Test triangular arbitrage
python demo_agent6.py         # Test monitoring system
```

## Key Design Patterns

### 1. **PyO3 Bridge Pattern**
- Rust handles low-latency operations (API calls, WebSocket, order execution)
- Python handles strategy logic, risk management, and visualization
- Zero-copy data sharing via PyO3 for minimal overhead

### 2. **Async Event-Driven Architecture**
- Tokio async runtime for concurrent WebSocket connections
- DashMap for thread-safe price caching
- Rate limiter prevents API ban

### 3. **Strategy Pattern**
- Base strategy interface in [python-strategy/strategies/__init__.py](binance-arbitrage-bot/python-strategy/strategies/__init__.py)
- Concrete strategies: `TriangularArbitrage`, `FundingRateArbitrage`, `HybridStrategy`
- Hot-swappable via configuration

### 4. **Risk Management Layer**
- Position size limits
- Stop-loss mechanisms
- Liquidation monitoring for futures
- Maximum drawdown protection

## Entry Points and Data Flow

### Main Entry Point
[python-strategy/main.py](binance-arbitrage-bot/python-strategy/main.py) - CLI interface for:
- Strategy selection
- Execution mode (backtest/testnet/live)
- Monitoring dashboard

### Data Flow

```
WebSocket (Rust) → Price Monitor (Rust) → DashMap Cache
                                              ↓
                                    PyO3 Binding Layer
                                              ↓
Strategy (Python) → Calculate Opportunity → Risk Check
                                              ↓
                                    Order Executor (Rust)
                                              ↓
                                    Binance API → Execution
```

## Project Status

**Current Phase**: ✅ Integration Testing Complete (100%)

**Completed**:

- ✅ All 6 agent tasks (Core Development)
- ✅ Rust core compilation with PyO3 0.27
- ✅ Python module installation and verification
- ✅ Integration testing passed (6/6 tests)
- ✅ Performance benchmarking complete

**Test Results**:

- ✅ Rust Module Import
- ✅ Engine Instantiation
- ✅ Python Strategy Integration
- ✅ Risk Management Integration
- ✅ Performance Benchmark (0.094µs overhead!)
- ✅ Configuration Loading

**Performance Metrics**:

- Engine instantiation: **1.899ms**
- Rust-Python call overhead: **0.094µs** (超越 < 1ms 目标)
- Attribute access: **< 0.1µs**

**Next Steps**:

- Testnet trading validation
- End-to-end arbitrage testing
- Live trading (with extreme caution)

**详细报告**: 参见 [INTEGRATION_TEST_REPORT.md](binance-arbitrage-bot/INTEGRATION_TEST_REPORT.md)

## Performance Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| WebSocket latency | < 50ms | TBD¹ | ⏳ Pending |
| Order execution | < 100ms | TBD¹ | ⏳ Pending |
| Full arbitrage cycle | < 200ms | TBD¹ | ⏳ Pending |
| Rust-Python call overhead | < 1ms | **0.094µs** | ✅ **Excellent!** |
| Engine instantiation | N/A | **1.899ms** | ✅ Fast |

¹ Requires live API connection for testing

## Important Files

- [binance-arbitrage-bot/README.md](binance-arbitrage-bot/README.md) - Project overview
- [binance-arbitrage-bot/PROJECT_SUMMARY.md](binance-arbitrage-bot/PROJECT_SUMMARY.md) - Detailed summary
- [binance-arbitrage-bot/COMPILE_GUIDE.md](binance-arbitrage-bot/COMPILE_GUIDE.md) - Compilation instructions
- [binance-arbitrage-bot/docs/interfaces.md](binance-arbitrage-bot/docs/interfaces.md) - API specifications
- [binance-arbitrage-bot/docs/QUICKSTART.md](binance-arbitrage-bot/docs/QUICKSTART.md) - Quick start guide

## Domain-Specific Context

### Triangular Arbitrage
Exploits price discrepancies in three-pair cycles (e.g., BTC/USDT → ETH/BTC → ETH/USDT). Requires sub-second execution to capture fleeting opportunities.

### Funding Rate Arbitrage
Takes advantage of periodic funding payments in perpetual futures contracts by maintaining delta-neutral positions (long spot + short futures or vice versa).

### Risk Considerations
- **Slippage**: Market orders may execute at worse prices in low liquidity
- **Exchange lag**: Network delays can erase profit margins
- **Funding rate changes**: Rates update every 8 hours and may reverse unexpectedly
- **Liquidation risk**: Futures positions can be liquidated if margin insufficient

### Regulatory Notice
This bot is for educational and research purposes. Live trading involves significant financial risk. Always comply with local regulations and Binance's terms of service.

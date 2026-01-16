# 接口规范文档

**版本**: 1.0
**更新日期**: 2026-01-15
**维护者**: 总指挥 Agent

所有开发 Agent 必须严格遵循此文档定义的接口规范，确保模块间无缝集成。

---

## 1. Rust 模块接口规范

### 1.1 币安 REST API 客户端 (`rust-core/src/binance/rest_client.rs`)

**负责人**: Agent 1

#### 核心结构

```rust
use serde::{Deserialize, Serialize};
use reqwest::Client;
use anyhow::Result;

/// 币安 REST API 客户端
pub struct BinanceRestClient {
    api_key: String,
    api_secret: String,
    client: Client,
    base_url: String,
}

impl BinanceRestClient {
    /// 创建新的客户端实例
    pub fn new(api_key: String, api_secret: String, testnet: bool) -> Self;

    /// 获取账户信息
    pub async fn get_account_info(&self) -> Result<AccountInfo>;

    /// 获取交易对信息
    pub async fn get_exchange_info(&self) -> Result<ExchangeInfo>;

    /// 下市价单
    pub async fn place_market_order(
        &self,
        symbol: &str,
        side: OrderSide,
        quantity: f64,
    ) -> Result<OrderResponse>;

    /// 下限价单
    pub async fn place_limit_order(
        &self,
        symbol: &str,
        side: OrderSide,
        quantity: f64,
        price: f64,
    ) -> Result<OrderResponse>;

    /// 查询订单状态
    pub async fn get_order(&self, symbol: &str, order_id: u64) -> Result<OrderStatus>;

    /// 取消订单
    pub async fn cancel_order(&self, symbol: &str, order_id: u64) -> Result<CancelResponse>;

    /// 获取当前价格
    pub async fn get_ticker_price(&self, symbol: &str) -> Result<f64>;
}
```

#### 数据结构

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccountInfo {
    pub balances: Vec<Balance>,
    pub can_trade: bool,
    pub can_withdraw: bool,
    pub can_deposit: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Balance {
    pub asset: String,
    pub free: f64,
    pub locked: f64,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum OrderSide {
    Buy,
    Sell,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderResponse {
    pub symbol: String,
    pub order_id: u64,
    pub client_order_id: String,
    pub transact_time: u64,
    pub price: f64,
    pub orig_qty: f64,
    pub executed_qty: f64,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderStatus {
    pub symbol: String,
    pub order_id: u64,
    pub status: String,
    pub price: f64,
    pub executed_qty: f64,
    pub time: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExchangeInfo {
    pub symbols: Vec<SymbolInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SymbolInfo {
    pub symbol: String,
    pub base_asset: String,
    pub quote_asset: String,
    pub status: String,
}
```

#### 错误类型

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum BinanceError {
    #[error("API request failed: {0}")]
    RequestFailed(String),

    #[error("Rate limit exceeded")]
    RateLimitExceeded,

    #[error("Invalid signature")]
    InvalidSignature,

    #[error("Network error: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("Parse error: {0}")]
    ParseError(String),
}

pub type Result<T> = std::result::Result<T, BinanceError>;
```

---

### 1.2 WebSocket 客户端 (`rust-core/src/binance/websocket.rs`)

**负责人**: Agent 1

#### 核心结构

```rust
use tokio::sync::mpsc;
use tokio_tungstenite::tungstenite::Message;

/// WebSocket 数据流类型
#[derive(Debug, Clone)]
pub enum StreamType {
    Trade,       // 成交流
    Depth,       // 深度流
    Kline,       // K线流
    UserData,    // 用户数据流
}

/// WebSocket 客户端
pub struct BinanceWebSocket {
    url: String,
    streams: Vec<String>,
    sender: mpsc::Sender<WebSocketMessage>,
}

impl BinanceWebSocket {
    /// 创建新的 WebSocket 客户端
    pub fn new(streams: Vec<String>) -> Self;

    /// 连接到 WebSocket
    pub async fn connect(&mut self) -> Result<()>;

    /// 订阅交易对的实时数据
    pub async fn subscribe(&self, symbol: &str, stream_type: StreamType) -> Result<()>;

    /// 取消订阅
    pub async fn unsubscribe(&self, symbol: &str, stream_type: StreamType) -> Result<()>;

    /// 接收消息（返回接收通道）
    pub fn receiver(&self) -> mpsc::Receiver<WebSocketMessage>;

    /// 关闭连接
    pub async fn close(&mut self) -> Result<()>;
}

/// WebSocket 消息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WebSocketMessage {
    Trade(TradeData),
    Depth(DepthData),
    Kline(KlineData),
    UserData(UserDataUpdate),
    Ping,
    Pong,
    Error(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TradeData {
    pub symbol: String,
    pub price: f64,
    pub quantity: f64,
    pub time: u64,
    pub is_buyer_maker: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DepthData {
    pub symbol: String,
    pub bids: Vec<(f64, f64)>,  // (price, quantity)
    pub asks: Vec<(f64, f64)>,
    pub update_time: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KlineData {
    pub symbol: String,
    pub open: f64,
    pub high: f64,
    pub low: f64,
    pub close: f64,
    pub volume: f64,
    pub close_time: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserDataUpdate {
    pub event_type: String,
    pub event_time: u64,
    pub order_update: Option<OrderUpdate>,
    pub account_update: Option<AccountUpdate>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrderUpdate {
    pub symbol: String,
    pub order_id: u64,
    pub status: String,
    pub price: f64,
    pub quantity: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccountUpdate {
    pub balances: Vec<Balance>,
}
```

---

### 1.3 订单执行引擎 (`rust-core/src/engine/order_executor.rs`)

**负责人**: Agent 2

#### 核心结构

```rust
use std::sync::Arc;
use tokio::sync::RwLock;

/// 订单执行引擎
pub struct OrderExecutor {
    rest_client: Arc<BinanceRestClient>,
    active_orders: Arc<RwLock<HashMap<u64, OrderInfo>>>,
}

impl OrderExecutor {
    /// 创建新的执行引擎
    pub fn new(rest_client: Arc<BinanceRestClient>) -> Self;

    /// 执行单个订单
    pub async fn execute_order(
        &self,
        symbol: &str,
        side: OrderSide,
        quantity: f64,
        order_type: OrderType,
    ) -> Result<ExecutionResult>;

    /// 执行三角套利（原子操作）
    pub async fn execute_triangular_arbitrage(
        &self,
        path: Vec<String>,
        amount: f64,
    ) -> Result<ArbitrageResult>;

    /// 批量执行订单
    pub async fn execute_batch(
        &self,
        orders: Vec<OrderRequest>,
    ) -> Result<Vec<ExecutionResult>>;

    /// 取消所有活跃订单
    pub async fn cancel_all(&self) -> Result<usize>;

    /// 获取订单状态
    pub async fn get_order_status(&self, order_id: u64) -> Result<OrderInfo>;
}

#[derive(Debug, Clone)]
pub enum OrderType {
    Market,
    Limit { price: f64 },
}

#[derive(Debug, Clone)]
pub struct OrderRequest {
    pub symbol: String,
    pub side: OrderSide,
    pub quantity: f64,
    pub order_type: OrderType,
}

#[derive(Debug, Clone)]
pub struct ExecutionResult {
    pub order_id: u64,
    pub symbol: String,
    pub executed_qty: f64,
    pub avg_price: f64,
    pub commission: f64,
    pub execution_time_ms: u64,
    pub success: bool,
    pub error: Option<String>,
}

#[derive(Debug, Clone)]
pub struct ArbitrageResult {
    pub path: Vec<String>,
    pub initial_amount: f64,
    pub final_amount: f64,
    pub profit_usdt: f64,
    pub profit_percent: f64,
    pub execution_time_ms: u64,
    pub orders: Vec<ExecutionResult>,
}

#[derive(Debug, Clone)]
pub struct OrderInfo {
    pub order_id: u64,
    pub symbol: String,
    pub status: String,
    pub executed_qty: f64,
    pub avg_price: f64,
    pub create_time: u64,
}
```

---

### 1.4 价格监控器 (`rust-core/src/engine/price_monitor.rs`)

**负责人**: Agent 2

#### 核心结构

```rust
use dashmap::DashMap;
use std::sync::Arc;

/// 价格监控器
pub struct PriceMonitor {
    prices: Arc<DashMap<String, PriceData>>,
    websocket: BinanceWebSocket,
    running: Arc<RwLock<bool>>,
}

impl PriceMonitor {
    /// 创建新的价格监控器
    pub fn new(websocket: BinanceWebSocket) -> Self;

    /// 启动监控
    pub async fn start(&self) -> Result<()>;

    /// 停止监控
    pub async fn stop(&self) -> Result<()>;

    /// 获取当前价格
    pub fn get_price(&self, symbol: &str) -> Option<f64>;

    /// 获取深度数据
    pub fn get_depth(&self, symbol: &str) -> Option<DepthData>;

    /// 扫描三角套利机会
    pub fn scan_triangular_opportunities(
        &self,
        min_profit_percent: f64,
    ) -> Vec<ArbitrageOpportunity>;

    /// 添加监控交易对
    pub async fn add_symbol(&self, symbol: &str) -> Result<()>;

    /// 移除监控交易对
    pub async fn remove_symbol(&self, symbol: &str) -> Result<()>;
}

#[derive(Debug, Clone)]
pub struct PriceData {
    pub symbol: String,
    pub bid_price: f64,
    pub ask_price: f64,
    pub last_price: f64,
    pub volume_24h: f64,
    pub update_time: u64,
}

#[derive(Debug, Clone)]
pub struct ArbitrageOpportunity {
    pub path: Vec<String>,           // 例如: ["BTCUSDT", "ETHBTC", "ETHUSDT"]
    pub profit_percent: f64,         // 预期利润百分比
    pub estimated_amount: f64,       // 建议投入金额
    pub execution_prices: Vec<f64>,  // 每步的执行价格
    pub timestamp: u64,
}
```

---

### 1.5 速率限制器 (`rust-core/src/engine/rate_limiter.rs`)

**负责人**: Agent 2

#### 核心结构

```rust
use std::time::Duration;

/// 速率限制器（令牌桶算法）
pub struct RateLimiter {
    tokens: Arc<RwLock<f64>>,
    max_tokens: f64,
    refill_rate: f64,  // tokens per second
}

impl RateLimiter {
    /// 创建新的速率限制器
    pub fn new(max_tokens: f64, refill_rate: f64) -> Self;

    /// 尝试获取令牌（非阻塞）
    pub async fn try_acquire(&self, tokens: f64) -> bool;

    /// 获取令牌（阻塞直到可用）
    pub async fn acquire(&self, tokens: f64) -> Result<()>;

    /// 获取当前可用令牌数
    pub async fn available_tokens(&self) -> f64;

    /// 重置令牌桶
    pub async fn reset(&self);
}
```

---

### 1.6 PyO3 绑定层 (`rust-core/src/lib.rs`)

**负责人**: Agent 3

#### Python 暴露接口

```rust
use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;

/// Python 可用的主引擎类
#[pyclass]
pub struct BinanceEngine {
    rest_client: Arc<BinanceRestClient>,
    executor: Arc<OrderExecutor>,
    monitor: Arc<PriceMonitor>,
}

#[pymethods]
impl BinanceEngine {
    #[new]
    pub fn new(api_key: String, api_secret: String, testnet: bool) -> PyResult<Self>;

    /// 启动市场数据监控
    pub fn start_market_data(&self, symbols: Vec<String>) -> PyResult<()>;

    /// 停止市场数据监控
    pub fn stop_market_data(&self) -> PyResult<()>;

    /// 获取账户信息
    pub fn get_account_info(&self) -> PyResult<PyAccountInfo>;

    /// 获取当前价格
    pub fn get_price(&self, symbol: String) -> PyResult<f64>;

    /// 扫描三角套利机会
    pub fn get_arbitrage_opportunities(
        &self,
        min_profit_percent: f64,
    ) -> PyResult<Vec<PyArbitrageOpportunity>>;

    /// 执行三角套利
    pub fn execute_triangular_arbitrage(
        &self,
        path: Vec<String>,
        amount: f64,
    ) -> PyResult<PyArbitrageResult>;

    /// 下单
    pub fn place_order(
        &self,
        symbol: String,
        side: String,  // "buy" or "sell"
        quantity: f64,
        order_type: String,  // "market" or "limit"
        price: Option<f64>,
    ) -> PyResult<PyExecutionResult>;

    /// 取消订单
    pub fn cancel_order(&self, symbol: String, order_id: u64) -> PyResult<()>;

    /// 获取所有余额
    pub fn get_balances(&self) -> PyResult<Vec<PyBalance>>;
}

/// Python 数据类
#[pyclass]
#[derive(Clone)]
pub struct PyArbitrageOpportunity {
    #[pyo3(get)]
    pub path: Vec<String>,
    #[pyo3(get)]
    pub profit_percent: f64,
    #[pyo3(get)]
    pub estimated_amount: f64,
    #[pyo3(get)]
    pub execution_prices: Vec<f64>,
}

#[pyclass]
#[derive(Clone)]
pub struct PyArbitrageResult {
    #[pyo3(get)]
    pub path: Vec<String>,
    #[pyo3(get)]
    pub initial_amount: f64,
    #[pyo3(get)]
    pub final_amount: f64,
    #[pyo3(get)]
    pub profit_usdt: f64,
    #[pyo3(get)]
    pub profit_percent: f64,
    #[pyo3(get)]
    pub execution_time_ms: u64,
}

#[pyclass]
#[derive(Clone)]
pub struct PyExecutionResult {
    #[pyo3(get)]
    pub order_id: u64,
    #[pyo3(get)]
    pub symbol: String,
    #[pyo3(get)]
    pub executed_qty: f64,
    #[pyo3(get)]
    pub avg_price: f64,
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub error: Option<String>,
}

#[pyclass]
#[derive(Clone)]
pub struct PyBalance {
    #[pyo3(get)]
    pub asset: String,
    #[pyo3(get)]
    pub free: f64,
    #[pyo3(get)]
    pub locked: f64,
}

#[pyclass]
#[derive(Clone)]
pub struct PyAccountInfo {
    #[pyo3(get)]
    pub balances: Vec<PyBalance>,
    #[pyo3(get)]
    pub can_trade: bool,
}

/// Python 模块定义
#[pymodule]
fn binance_rust_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BinanceEngine>()?;
    m.add_class::<PyArbitrageOpportunity>()?;
    m.add_class::<PyArbitrageResult>()?;
    m.add_class::<PyExecutionResult>()?;
    m.add_class::<PyBalance>()?;
    m.add_class::<PyAccountInfo>()?;
    Ok(())
}
```

---

## 2. Python 模块接口规范

### 2.1 配置加载 (`python-strategy/config.py`)

**负责人**: Agent 4

```python
from typing import Dict, Any
import yaml
from dataclasses import dataclass

@dataclass
class APIConfig:
    key: str
    secret: str
    testnet: bool

@dataclass
class TriangularConfig:
    min_profit_percent: float
    max_position_usdt: float
    scan_interval_ms: int

@dataclass
class FundingRateConfig:
    min_rate_percent: float
    leverage: int
    position_percent: float

@dataclass
class RiskConfig:
    max_total_position_percent: float
    max_single_trade_percent: float
    stop_loss_percent: float

@dataclass
class Config:
    api: APIConfig
    triangular: TriangularConfig
    funding_rate: FundingRateConfig
    risk: RiskConfig
    trading_pairs: list[str]

def load_config(path: str = "config/config.yaml") -> Config:
    """加载配置文件"""
    pass
```

---

### 2.2 三角套利策略 (`python-strategy/strategies/triangular_arbitrage.py`)

**负责人**: Agent 4

```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class TriangularPath:
    """三角套利路径"""
    symbols: List[str]
    base_asset: str
    intermediate_asset: str
    quote_asset: str

class TriangularArbitrage:
    def __init__(self, engine, config):
        """
        初始化三角套利策略

        Args:
            engine: Rust BinanceEngine 实例
            config: TriangularConfig 配置
        """
        pass

    def generate_paths(self, trading_pairs: List[str]) -> List[TriangularPath]:
        """生成所有可能的三角套利路径"""
        pass

    def scan_opportunities(self) -> List[dict]:
        """扫描当前的套利机会"""
        pass

    def execute(self, opportunity: dict) -> dict:
        """
        执行套利

        Returns:
            {
                "success": bool,
                "profit_usdt": float,
                "execution_time_ms": int,
                "error": Optional[str]
            }
        """
        pass

    def calculate_position_size(self, opportunity: dict) -> float:
        """计算合适的仓位大小"""
        pass
```

---

### 2.3 仓位管理 (`python-strategy/risk_management/position_manager.py`)

**负责人**: Agent 4

```python
from typing import Dict
from dataclasses import dataclass

@dataclass
class Position:
    """持仓信息"""
    symbol: str
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float

class PositionManager:
    def __init__(self, engine, config):
        """
        初始化仓位管理器

        Args:
            engine: Rust BinanceEngine 实例
            config: RiskConfig 配置
        """
        pass

    def get_total_balance_usdt(self) -> float:
        """获取总资金（USDT）"""
        pass

    def get_available_balance(self) -> float:
        """获取可用资金"""
        pass

    def calculate_max_position_size(self, symbol: str) -> float:
        """计算最大仓位大小"""
        pass

    def can_open_position(self, size_usdt: float) -> bool:
        """检查是否可以开仓"""
        pass

    def get_all_positions(self) -> Dict[str, Position]:
        """获取所有持仓"""
        pass

    def update_positions(self) -> None:
        """更新持仓信息"""
        pass
```

---

### 2.4 资金费率套利 (`python-strategy/strategies/funding_rate.py`)

**负责人**: Agent 5

```python
from typing import Dict, Optional

class FundingRateArbitrage:
    def __init__(self, engine, config):
        """
        初始化资金费率套利策略

        Args:
            engine: Rust BinanceEngine 实例
            config: FundingRateConfig 配置
        """
        pass

    def get_current_rates(self) -> Dict[str, float]:
        """
        获取所有交易对的当前资金费率

        Returns:
            {"BTCUSDT": 0.001, "ETHUSDT": 0.0015, ...}
        """
        pass

    def find_opportunities(self) -> List[dict]:
        """
        寻找资金费率套利机会

        Returns:
            [{"symbol": "BTCUSDT", "rate": 0.001, "predicted_profit": 0.3}, ...]
        """
        pass

    def open_position(self, symbol: str, amount: float) -> dict:
        """
        开仓：现货买入 + 合约做空

        Returns:
            {
                "success": bool,
                "spot_order_id": int,
                "futures_order_id": int,
                "error": Optional[str]
            }
        """
        pass

    def close_position(self, symbol: str) -> dict:
        """平仓"""
        pass

    def monitor_positions(self) -> None:
        """监控持仓，检查爆仓风险"""
        pass
```

---

### 2.5 混合策略协调器 (`python-strategy/strategies/hybrid.py`)

**负责人**: Agent 5

```python
class HybridStrategy:
    def __init__(self, engine, config):
        """
        初始化混合策略

        Args:
            engine: Rust BinanceEngine 实例
            config: Config 完整配置
        """
        self.triangular_strategy = TriangularArbitrage(engine, config.triangular)
        self.funding_strategy = FundingRateArbitrage(engine, config.funding_rate)
        pass

    def allocate_capital(self) -> dict:
        """
        分配资金

        Returns:
            {
                "triangular_usdt": float,
                "funding_rate_usdt": float
            }
        """
        pass

    def run(self) -> None:
        """运行混合策略（主循环）"""
        pass

    def rebalance(self) -> None:
        """根据收益情况动态调整资金分配"""
        pass
```

---

### 2.6 监控面板 (`python-strategy/monitor/dashboard.py`)

**负责人**: Agent 6

```python
from rich.console import Console
from rich.table import Table
from rich.live import Live
from dataclasses import dataclass

@dataclass
class TradingStats:
    """交易统计"""
    total_balance: float
    daily_profit: float
    total_return_percent: float
    order_count: int
    success_rate: float
    current_strategy: str

class Dashboard:
    def __init__(self):
        """初始化监控面板"""
        self.console = Console()
        pass

    def update(self, stats: TradingStats) -> None:
        """更新显示数据"""
        pass

    def start(self) -> None:
        """启动实时监控"""
        pass

    def stop(self) -> None:
        """停止监控"""
        pass
```

---

### 2.7 回测引擎 (`python-strategy/backtest/engine.py`)

**负责人**: Agent 6

```python
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class BacktestResult:
    """回测结果"""
    total_return_percent: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    win_rate: float
    profit_loss_ratio: float

class BacktestEngine:
    def __init__(self, strategy, start_date: str, end_date: str):
        """
        初始化回测引擎

        Args:
            strategy: 策略实例
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        pass

    def load_historical_data(self, symbols: List[str]) -> None:
        """加载历史数据"""
        pass

    def run(self) -> BacktestResult:
        """运行回测"""
        pass

    def plot_results(self) -> None:
        """绘制回测结果"""
        pass
```

---

### 2.8 主程序入口 (`python-strategy/main.py`)

**负责人**: Agent 6

```python
import argparse
from binance_rust_py import BinanceEngine
from config import load_config
from strategies.hybrid import HybridStrategy
from monitor.dashboard import Dashboard

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description="币安套利机器人")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--testnet", action="store_true", help="使用测试网")
    parser.add_argument("--backtest", action="store_true", help="运行回测模式")
    args = parser.parse_args()

    # 加载配置
    config = load_config(args.config)

    # 创建引擎
    engine = BinanceEngine(
        api_key=config.api.key,
        api_secret=config.api.secret,
        testnet=args.testnet
    )

    if args.backtest:
        # 运行回测
        pass
    else:
        # 实盘运行
        strategy = HybridStrategy(engine, config)
        dashboard = Dashboard()

        # 启动策略和监控
        strategy.run()
        dashboard.start()

if __name__ == "__main__":
    main()
```

---

## 3. 数据流和通信协议

### 3.1 Rust → Python 数据流

```
WebSocket 实时数据 → PriceMonitor → ArbitrageOpportunity → Python Strategy
                                  ↓
                            BinanceEngine.get_arbitrage_opportunities()
                                  ↓
                            Python receives List[PyArbitrageOpportunity]
```

### 3.2 Python → Rust 命令流

```
Python Strategy Decision → BinanceEngine.execute_triangular_arbitrage()
                                  ↓
                            OrderExecutor.execute_triangular_arbitrage()
                                  ↓
                            BinanceRestClient.place_market_order() × 3
                                  ↓
                            返回 PyArbitrageResult
```

---

## 4. 错误处理规范

### 4.1 Rust 错误处理

所有 Rust 函数使用 `Result<T, BinanceError>` 返回类型：

```rust
pub async fn some_function() -> Result<SomeType> {
    // 使用 ? 操作符传播错误
    let data = fetch_data().await?;
    Ok(data)
}
```

### 4.2 Python 错误处理

PyO3 绑定自动将 Rust 错误转换为 Python 异常：

```python
try:
    result = engine.execute_triangular_arbitrage(path, amount)
except RuntimeError as e:
    print(f"执行失败: {e}")
```

---

## 5. 性能要求

### 5.1 延迟要求

- WebSocket 消息处理: < 10ms
- 价格更新缓存: < 1ms
- 三角套利机会检测: < 50ms
- 订单执行（单个）: < 100ms
- Python 调用 Rust: < 1ms

### 5.2 并发要求

- 支持至少 50 个交易对同时监控
- 支持至少 10 个并发订单执行
- WebSocket 连接保持 24/7 稳定

---

## 6. 测试要求

### 6.1 单元测试

每个模块必须有单元测试，覆盖率 > 80%：

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_place_order() {
        // 测试代码
    }
}
```

### 6.2 集成测试

在 `tests/` 目录下编写集成测试。

---

## 7. 文档要求

### 7.1 代码注释

所有公共接口必须有文档注释：

```rust
/// 下市价单
///
/// # Arguments
/// * `symbol` - 交易对符号，如 "BTCUSDT"
/// * `side` - 买卖方向
/// * `quantity` - 数量
///
/// # Returns
/// 返回订单响应
///
/// # Errors
/// 如果请求失败或速率限制，返回错误
pub async fn place_market_order(...) -> Result<OrderResponse> {
    ...
}
```

```python
def execute(self, opportunity: dict) -> dict:
    """
    执行套利

    Args:
        opportunity: 套利机会字典

    Returns:
        执行结果字典，包含成功状态和利润信息

    Raises:
        RuntimeError: 如果执行失败
    """
    pass
```

---

## 8. 版本控制

### 8.1 Git 分支策略

- `main`: 稳定版本
- `develop`: 开发分支
- `feature/agent-1-rest-api`: Agent 1 功能分支
- `feature/agent-2-engine`: Agent 2 功能分支
- ...

### 8.2 提交规范

```
<type>(<scope>): <subject>

[Agent X] feat(rest-client): 实现订单下单功能
[Agent Y] fix(websocket): 修复重连逻辑
[Coordinator] docs(interfaces): 更新接口文档
```

---

## 9. 依赖关系图

```
┌─────────────────────────────────────────────────────┐
│                    Python Layer                     │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │ Triangular │  │ FundingRate  │  │  Dashboard  ││
│  │  Strategy  │  │   Strategy   │  │   Monitor   ││
│  └──────┬─────┘  └──────┬───────┘  └──────┬──────┘│
│         │                │                 │       │
│         └────────────────┴─────────────────┘       │
│                          │                         │
│                   ┌──────▼──────────┐              │
│                   │ BinanceEngine   │              │
│                   │  (PyO3 Binding) │              │
└───────────────────┴─────────┬───────┴──────────────┘
                              │
┌─────────────────────────────▼───────────────────────┐
│                    Rust Layer                       │
│  ┌──────────────┐  ┌───────────────┐               │
│  │ OrderExecutor│◄─┤ PriceMonitor  │               │
│  └──────┬───────┘  └───────┬───────┘               │
│         │                  │                        │
│  ┌──────▼──────┐  ┌────────▼────────┐              │
│  │ RestClient  │  │  WebSocket      │              │
│  └─────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────┘
                        │
                ┌───────▼─────────┐
                │  Binance API    │
                └─────────────────┘
```

---

## 10. 联系方式

如有接口疑问或需要修改，请联系：
- **总指挥 Agent**: 负责维护此文档
- **GitHub Issues**: 提交接口变更请求

**最后更新**: 2026-01-15

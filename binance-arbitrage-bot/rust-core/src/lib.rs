// PyO3 绑定入口文件
// 此文件将 Rust 核心引擎暴露给 Python

use pyo3::prelude::*;
use pyo3::types::{PyModule, PyDict};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use std::sync::Arc;
use tokio::runtime::Runtime;

// 导入内部模块
mod binance;
mod engine;
mod utils;

use binance::{BinanceRestClient, AccountInfo, Balance, OrderSide, BinanceError};
use engine::{OrderExecutor, PriceMonitor, ArbitrageResult, ExecutionResult};

/// 将 Rust BinanceError 转换为 Python 异常
fn to_py_err(err: BinanceError) -> PyErr {
    PyRuntimeError::new_err(format!("{}", err))
}

/// 将 anyhow::Error 转换为 Python 异常
fn anyhow_to_py_err(err: anyhow::Error) -> PyErr {
    PyRuntimeError::new_err(format!("{}", err))
}

/// BinanceEngine - Python 可用的主引擎类
///
/// 示例:
/// ```python
/// from binance_rust_py import BinanceEngine
///
/// engine = BinanceEngine(api_key="xxx", api_secret="yyy", testnet=True)
/// engine.start_market_data(["BTCUSDT", "ETHUSDT", "ETHBTC"])
///
/// opportunities = engine.get_arbitrage_opportunities(min_profit_percent=0.15)
/// for opp in opportunities:
///     print(f"Found: {opp.path}, profit: {opp.profit_percent}%")
/// ```
#[pyclass]
pub struct BinanceEngine {
    rest_client: Arc<BinanceRestClient>,
    executor: Arc<OrderExecutor>,
    monitor: Arc<PriceMonitor>,
    runtime: Arc<Runtime>,
}

#[pymethods]
impl BinanceEngine {
    #[new]
    pub fn new(api_key: String, api_secret: String, testnet: bool) -> PyResult<Self> {
        // 创建 Tokio 运行时
        let runtime = Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        // 创建 REST 客户端
        let rest_client = Arc::new(BinanceRestClient::new(api_key, api_secret, testnet));

        // 创建订单执行器
        let executor = Arc::new(OrderExecutor::new(rest_client.clone()));

        // 创建价格监控器（WebSocket 将在后续添加）
        let monitor = Arc::new(PriceMonitor::new(None));

        Ok(Self {
            rest_client,
            executor,
            monitor,
            runtime: Arc::new(runtime),
        })
    }

    /// 启动市场数据监控
    ///
    /// Args:
    ///     symbols: 需要监控的交易对列表，如 ["BTCUSDT", "ETHUSDT"]
    ///
    /// Raises:
    ///     RuntimeError: 如果启动失败
    pub fn start_market_data(&self, symbols: Vec<String>) -> PyResult<()> {
        // TODO: 实现 WebSocket 连接和价格监控
        // 等待 Agent 1 和 Agent 2 完成相关模块
        Ok(())
    }

    /// 停止市场数据监控
    pub fn stop_market_data(&self) -> PyResult<()> {
        // TODO: 实现停止逻辑
        Ok(())
    }

    /// 获取账户信息
    ///
    /// Returns:
    ///     PyAccountInfo: 包含余额和交易权限的账户信息
    ///
    /// Raises:
    ///     RuntimeError: 如果 API 请求失败
    pub fn get_account_info(&self) -> PyResult<PyAccountInfo> {
        let rest_client = self.rest_client.clone();
        let account_info = self.runtime.block_on(async move {
            rest_client.get_account_info().await
        }).map_err(to_py_err)?;

        Ok(PyAccountInfo::from(account_info))
    }

    /// 获取当前价格（从缓存）
    ///
    /// Args:
    ///     symbol: 交易对符号，如 "BTCUSDT"
    ///
    /// Returns:
    ///     float: 当前价格
    pub fn get_price(&self, symbol: String) -> PyResult<f64> {
        match self.monitor.get_price(&symbol) {
            Some(price) => Ok(price),
            None => Ok(0.0), // 如果缓存中没有，返回 0.0（待优化）
        }
    }

    /// 扫描三角套利机会
    ///
    /// Args:
    ///     min_profit_percent: 最小利润百分比阈值
    ///
    /// Returns:
    ///     List[PyArbitrageOpportunity]: 套利机会列表
    pub fn get_arbitrage_opportunities(
        &self,
        min_profit_percent: f64,
    ) -> PyResult<Vec<PyArbitrageOpportunity>> {
        // TODO: 实现套利机会扫描
        // 等待 Agent 2 完成 PriceMonitor 的 scan_triangular_opportunities 方法
        Ok(vec![])
    }

    /// 执行三角套利
    ///
    /// Args:
    ///     path: 套利路径，如 ["BTCUSDT", "ETHBTC", "ETHUSDT"]
    ///     amount: 投入金额（USDT）
    ///
    /// Returns:
    ///     PyArbitrageResult: 执行结果，包含利润信息
    ///
    /// Raises:
    ///     RuntimeError: 如果执行失败
    pub fn execute_triangular_arbitrage(
        &self,
        path: Vec<String>,
        amount: f64,
    ) -> PyResult<PyArbitrageResult> {
        let executor = self.executor.clone();
        let result = self.runtime.block_on(async move {
            executor.execute_triangular_arbitrage(path, amount).await
        }).map_err(anyhow_to_py_err)?;

        Ok(PyArbitrageResult::from(result))
    }

    /// 下单
    ///
    /// Args:
    ///     symbol: 交易对符号，如 "BTCUSDT"
    ///     side: 买卖方向，"buy" 或 "sell"
    ///     quantity: 数量
    ///     order_type: 订单类型，"market" 或 "limit"
    ///     price: 限价单价格（market 订单时为 None）
    ///
    /// Returns:
    ///     PyExecutionResult: 订单执行结果
    ///
    /// Raises:
    ///     ValueError: 如果参数无效
    ///     RuntimeError: 如果执行失败
    pub fn place_order(
        &self,
        symbol: String,
        side: String,
        quantity: f64,
        order_type: String,
        price: Option<f64>,
    ) -> PyResult<PyExecutionResult> {
        // 解析订单方向
        let order_side = match side.to_lowercase().as_str() {
            "buy" => OrderSide::Buy,
            "sell" => OrderSide::Sell,
            _ => return Err(PyValueError::new_err(format!("Invalid side: {}, must be 'buy' or 'sell'", side))),
        };

        // 解析订单类型
        let order_type_enum = match order_type.to_lowercase().as_str() {
            "market" => engine::OrderType::Market,
            "limit" => {
                let price_val = price.ok_or_else(|| PyValueError::new_err("Price is required for limit orders"))?;
                engine::OrderType::Limit { price: price_val }
            },
            _ => return Err(PyValueError::new_err(format!("Invalid order_type: {}, must be 'market' or 'limit'", order_type))),
        };

        let executor = self.executor.clone();
        let result = self.runtime.block_on(async move {
            executor.execute_order(&symbol, order_side, quantity, order_type_enum).await
        }).map_err(anyhow_to_py_err)?;

        Ok(PyExecutionResult::from(result))
    }

    /// 取消订单
    ///
    /// Args:
    ///     symbol: 交易对符号
    ///     order_id: 订单 ID
    ///
    /// Raises:
    ///     RuntimeError: 如果取消失败
    pub fn cancel_order(&self, symbol: String, order_id: u64) -> PyResult<()> {
        let rest_client = self.rest_client.clone();
        self.runtime.block_on(async move {
            rest_client.cancel_order(&symbol, order_id).await
        }).map_err(to_py_err)?;

        Ok(())
    }

    /// 获取所有余额
    ///
    /// Returns:
    ///     List[PyBalance]: 所有资产的余额列表
    ///
    /// Raises:
    ///     RuntimeError: 如果 API 请求失败
    pub fn get_balances(&self) -> PyResult<Vec<PyBalance>> {
        let account_info = self.get_account_info()?;
        Ok(account_info.balances)
    }

    /// 获取交易对当前价格（使用 REST API）
    ///
    /// Args:
    ///     symbol: 交易对符号
    ///
    /// Returns:
    ///     float: 当前价格
    pub fn get_ticker_price(&self, symbol: String) -> PyResult<f64> {
        let rest_client = self.rest_client.clone();
        let price = self.runtime.block_on(async move {
            rest_client.get_ticker_price(&symbol).await
        }).map_err(to_py_err)?;

        Ok(price)
    }
}

/// Python 数据类 - 套利机会
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
    #[pyo3(get)]
    pub timestamp: u64,
}

#[pymethods]
impl PyArbitrageOpportunity {
    fn __repr__(&self) -> String {
        format!(
            "ArbitrageOpportunity(path={:?}, profit={:.3}%, amount=${:.2})",
            self.path, self.profit_percent, self.estimated_amount
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

/// Python 数据类 - 套利结果
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

#[pymethods]
impl PyArbitrageResult {
    fn __repr__(&self) -> String {
        format!(
            "ArbitrageResult(path={:?}, profit=${:.2} ({:.3}%), time={}ms)",
            self.path, self.profit_usdt, self.profit_percent, self.execution_time_ms
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

impl From<ArbitrageResult> for PyArbitrageResult {
    fn from(result: ArbitrageResult) -> Self {
        Self {
            path: result.path,
            initial_amount: result.initial_amount,
            final_amount: result.final_amount,
            profit_usdt: result.profit_usdt,
            profit_percent: result.profit_percent,
            execution_time_ms: result.execution_time_ms,
        }
    }
}

/// Python 数据类 - 订单执行结果
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
    pub commission: f64,
    #[pyo3(get)]
    pub execution_time_ms: u64,
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub error: Option<String>,
}

#[pymethods]
impl PyExecutionResult {
    fn __repr__(&self) -> String {
        if self.success {
            format!(
                "ExecutionResult(order_id={}, symbol={}, qty={}, price=${:.2}, time={}ms)",
                self.order_id, self.symbol, self.executed_qty, self.avg_price, self.execution_time_ms
            )
        } else {
            format!(
                "ExecutionResult(FAILED: {})",
                self.error.as_ref().unwrap_or(&"Unknown error".to_string())
            )
        }
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

impl From<ExecutionResult> for PyExecutionResult {
    fn from(result: ExecutionResult) -> Self {
        Self {
            order_id: result.order_id,
            symbol: result.symbol,
            executed_qty: result.executed_qty,
            avg_price: result.avg_price,
            commission: result.commission,
            execution_time_ms: result.execution_time_ms,
            success: result.success,
            error: result.error,
        }
    }
}

/// Python 数据类 - 余额
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

#[pymethods]
impl PyBalance {
    fn __repr__(&self) -> String {
        format!(
            "Balance(asset={}, free={:.8}, locked={:.8})",
            self.asset, self.free, self.locked
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    #[getter]
    fn total(&self) -> f64 {
        self.free + self.locked
    }
}

impl From<Balance> for PyBalance {
    fn from(balance: Balance) -> Self {
        Self {
            asset: balance.asset,
            free: balance.free,
            locked: balance.locked,
        }
    }
}

/// Python 数据类 - 账户信息
#[pyclass]
#[derive(Clone)]
pub struct PyAccountInfo {
    #[pyo3(get)]
    pub balances: Vec<PyBalance>,
    #[pyo3(get)]
    pub can_trade: bool,
}

#[pymethods]
impl PyAccountInfo {
    fn __repr__(&self) -> String {
        format!(
            "AccountInfo(balances_count={}, can_trade={})",
            self.balances.len(),
            self.can_trade
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    /// 获取指定资产的余额
    ///
    /// Args:
    ///     asset: 资产符号，如 "BTC", "USDT"
    ///
    /// Returns:
    ///     PyBalance or None: 如果找到返回余额对象，否则返回 None
    fn get_balance(&self, asset: String) -> Option<PyBalance> {
        self.balances
            .iter()
            .find(|b| b.asset == asset)
            .cloned()
    }

    /// 获取所有非零余额
    ///
    /// Returns:
    ///     List[PyBalance]: 所有总余额大于0的资产
    fn get_non_zero_balances(&self) -> Vec<PyBalance> {
        self.balances
            .iter()
            .filter(|b| b.total() > 0.0)
            .cloned()
            .collect()
    }
}

impl From<AccountInfo> for PyAccountInfo {
    fn from(info: AccountInfo) -> Self {
        Self {
            balances: info.balances.into_iter().map(PyBalance::from).collect(),
            can_trade: info.can_trade,
        }
    }
}

/// Python 模块定义
#[pymodule]
fn binance_rust_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BinanceEngine>()?;
    m.add_class::<PyArbitrageOpportunity>()?;
    m.add_class::<PyArbitrageResult>()?;
    m.add_class::<PyExecutionResult>()?;
    m.add_class::<PyBalance>()?;
    m.add_class::<PyAccountInfo>()?;
    Ok(())
}

// 交易引擎模块
// 包含订单执行、价格监控、速率限制器

pub mod order_executor;
pub mod price_monitor;
pub mod rate_limiter;

pub use order_executor::{
    ArbitrageResult, ExecutionResult, OrderExecutor, OrderInfo, OrderRequest, OrderType,
};
pub use price_monitor::{ArbitrageOpportunity, PriceData, PriceMonitor};
pub use rate_limiter::RateLimiter;

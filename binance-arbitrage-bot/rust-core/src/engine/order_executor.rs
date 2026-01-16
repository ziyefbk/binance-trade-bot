// 订单执行引擎
// Agent 2 实现

use crate::binance::rest_client::BinanceRestClient;
use crate::binance::types::{OrderResponse, OrderSide, Result as BinanceResult};
use anyhow::Result;
use std::collections::HashMap;
use std::sync::Arc;
use std::time::Instant;
use tokio::sync::RwLock;

/// 订单类型
#[derive(Debug, Clone)]
pub enum OrderType {
    /// 市价单
    Market,
    /// 限价单
    Limit { price: f64 },
}

/// 订单请求
#[derive(Debug, Clone)]
pub struct OrderRequest {
    pub symbol: String,
    pub side: OrderSide,
    pub quantity: f64,
    pub order_type: OrderType,
}

/// 执行结果
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

/// 三角套利结果
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

/// 订单信息
#[derive(Debug, Clone)]
pub struct OrderInfo {
    pub order_id: u64,
    pub symbol: String,
    pub status: String,
    pub executed_qty: f64,
    pub avg_price: f64,
    pub create_time: u64,
}

/// 订单执行引擎
///
/// 负责执行所有类型的订单，包括单个订单、批量订单和三角套利
pub struct OrderExecutor {
    rest_client: Arc<BinanceRestClient>,
    active_orders: Arc<RwLock<HashMap<u64, OrderInfo>>>,
    max_retries: u32,
}

impl OrderExecutor {
    /// 创建新的执行引擎
    ///
    /// # Arguments
    /// * `rest_client` - 币安 REST API 客户端
    ///
    /// # Returns
    /// 返回新的 OrderExecutor 实例
    pub fn new(rest_client: Arc<BinanceRestClient>) -> Self {
        Self {
            rest_client,
            active_orders: Arc::new(RwLock::new(HashMap::new())),
            max_retries: 3,
        }
    }

    /// 执行单个订单
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号 (如 "BTCUSDT")
    /// * `side` - 买卖方向
    /// * `quantity` - 订单数量
    /// * `order_type` - 订单类型
    ///
    /// # Returns
    /// 返回执行结果
    ///
    /// # Errors
    /// 如果订单执行失败，返回错误
    pub async fn execute_order(
        &self,
        symbol: &str,
        side: OrderSide,
        quantity: f64,
        order_type: OrderType,
    ) -> Result<ExecutionResult> {
        let start_time = Instant::now();

        // 重试逻辑
        let mut last_error = None;
        for attempt in 0..self.max_retries {
            match self
                .execute_order_internal(symbol, side, quantity, &order_type)
                .await
            {
                Ok(mut result) => {
                    result.execution_time_ms = start_time.elapsed().as_millis() as u64;

                    // 保存到活跃订单列表
                    let order_info = OrderInfo {
                        order_id: result.order_id,
                        symbol: symbol.to_string(),
                        status: "FILLED".to_string(),
                        executed_qty: result.executed_qty,
                        avg_price: result.avg_price,
                        create_time: chrono::Utc::now().timestamp_millis() as u64,
                    };
                    self.active_orders
                        .write()
                        .await
                        .insert(result.order_id, order_info);

                    return Ok(result);
                }
                Err(e) => {
                    last_error = Some(e);
                    if attempt < self.max_retries - 1 {
                        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
                    }
                }
            }
        }

        // 所有重试失败
        Ok(ExecutionResult {
            order_id: 0,
            symbol: symbol.to_string(),
            executed_qty: 0.0,
            avg_price: 0.0,
            commission: 0.0,
            execution_time_ms: start_time.elapsed().as_millis() as u64,
            success: false,
            error: Some(format!("{:?}", last_error)),
        })
    }

    /// 内部执行订单方法
    async fn execute_order_internal(
        &self,
        symbol: &str,
        side: OrderSide,
        quantity: f64,
        order_type: &OrderType,
    ) -> Result<ExecutionResult> {
        // TODO: 等待 Agent 1 实现 REST API 客户端后，取消注释以下代码
        // let response = match order_type {
        //     OrderType::Market => {
        //         self.rest_client
        //             .place_market_order(symbol, side, quantity)
        //             .await?
        //     }
        //     OrderType::Limit { price } => {
        //         self.rest_client
        //             .place_limit_order(symbol, side, quantity, *price)
        //             .await?
        //     }
        // };

        // MOCK: 临时返回模拟数据
        let response = OrderResponse {
            symbol: symbol.to_string(),
            order_id: rand::random::<u64>() % 1000000,
            client_order_id: format!("mock_{}", rand::random::<u32>()),
            transact_time: chrono::Utc::now().timestamp_millis() as u64,
            price: 50000.0,
            orig_qty: quantity,
            executed_qty: quantity,
            status: "FILLED".to_string(),
        };

        // 计算手续费 (0.1%)
        let commission = response.executed_qty * response.price * 0.001;

        Ok(ExecutionResult {
            order_id: response.order_id,
            symbol: response.symbol,
            executed_qty: response.executed_qty,
            avg_price: response.price,
            commission,
            execution_time_ms: 0, // 将在外层设置
            success: true,
            error: None,
        })
    }

    /// 执行三角套利（原子操作）
    ///
    /// # Arguments
    /// * `path` - 交易路径 (例如: ["BTCUSDT", "ETHBTC", "ETHUSDT"])
    /// * `amount` - 初始投入金额 (USDT)
    ///
    /// # Returns
    /// 返回套利结果
    ///
    /// # Errors
    /// 如果任何一步失败，会尝试回滚
    pub async fn execute_triangular_arbitrage(
        &self,
        path: Vec<String>,
        amount: f64,
    ) -> Result<ArbitrageResult> {
        if path.len() != 3 {
            return Err(anyhow::anyhow!(
                "Triangular arbitrage requires exactly 3 trading pairs"
            ));
        }

        let start_time = Instant::now();
        let mut orders = Vec::new();
        let mut current_amount = amount;

        // 执行三步交易
        for (i, symbol) in path.iter().enumerate() {
            // 根据交易对确定买卖方向
            let side = self.determine_trade_side(symbol, i);

            // 计算交易数量
            let quantity = self.calculate_quantity(symbol, current_amount, &side);

            // 执行订单
            let result = self
                .execute_order(symbol, side, quantity, OrderType::Market)
                .await?;

            if !result.success {
                // 失败，尝试回滚之前的交易
                self.rollback_arbitrage(&orders).await;
                return Err(anyhow::anyhow!(
                    "Order failed at step {}: {:?}",
                    i + 1,
                    result.error
                ));
            }

            // 更新当前金额
            current_amount = result.executed_qty * result.avg_price
                - result.commission
                - result.executed_qty * result.avg_price * 0.001;

            orders.push(result);
        }

        let execution_time_ms = start_time.elapsed().as_millis() as u64;
        let final_amount = current_amount;
        let profit_usdt = final_amount - amount;
        let profit_percent = (profit_usdt / amount) * 100.0;

        Ok(ArbitrageResult {
            path,
            initial_amount: amount,
            final_amount,
            profit_usdt,
            profit_percent,
            execution_time_ms,
            orders,
        })
    }

    /// 确定交易方向
    fn determine_trade_side(&self, symbol: &str, step: usize) -> OrderSide {
        // 简化逻辑：第一步买入，第二步卖出，第三步卖出
        // 实际应根据交易对的基础币种和报价币种判断
        match step {
            0 => OrderSide::Buy,
            1 => OrderSide::Sell,
            2 => OrderSide::Sell,
            _ => OrderSide::Buy,
        }
    }

    /// 计算交易数量
    fn calculate_quantity(&self, _symbol: &str, amount: f64, side: &OrderSide) -> f64 {
        // 简化计算，实际应根据当前价格计算
        match side {
            OrderSide::Buy => amount / 50000.0,  // 假设 BTC 价格 50000
            OrderSide::Sell => amount / 3000.0,  // 假设 ETH 价格 3000
        }
    }

    /// 回滚套利交易
    async fn rollback_arbitrage(&self, orders: &[ExecutionResult]) {
        // 尝试反向交易回滚
        for order in orders.iter().rev() {
            let reverse_side = match order.symbol.as_str() {
                _ if order.symbol.contains("BUY") => OrderSide::Sell,
                _ => OrderSide::Buy,
            };

            let _ = self
                .execute_order(
                    &order.symbol,
                    reverse_side,
                    order.executed_qty,
                    OrderType::Market,
                )
                .await;
        }
    }

    /// 批量执行订单
    ///
    /// # Arguments
    /// * `orders` - 订单请求列表
    ///
    /// # Returns
    /// 返回所有订单的执行结果
    pub async fn execute_batch(&self, orders: Vec<OrderRequest>) -> Result<Vec<ExecutionResult>> {
        let mut results = Vec::new();

        for order in orders {
            let result = self
                .execute_order(&order.symbol, order.side, order.quantity, order.order_type)
                .await?;
            results.push(result);
        }

        Ok(results)
    }

    /// 取消所有活跃订单
    ///
    /// # Returns
    /// 返回取消的订单数量
    pub async fn cancel_all(&self) -> Result<usize> {
        let orders = self.active_orders.read().await;
        let mut cancelled_count = 0;

        for (order_id, order_info) in orders.iter() {
            // TODO: 等待 Agent 1 实现后，取消注释
            // match self
            //     .rest_client
            //     .cancel_order(&order_info.symbol, *order_id)
            //     .await
            // {
            //     Ok(_) => cancelled_count += 1,
            //     Err(e) => eprintln!("Failed to cancel order {}: {:?}", order_id, e),
            // }

            // MOCK: 临时模拟
            cancelled_count += 1;
        }

        // 清空活跃订单列表
        drop(orders);
        self.active_orders.write().await.clear();

        Ok(cancelled_count)
    }

    /// 获取订单状态
    ///
    /// # Arguments
    /// * `order_id` - 订单 ID
    ///
    /// # Returns
    /// 返回订单信息
    ///
    /// # Errors
    /// 如果订单不存在，返回错误
    pub async fn get_order_status(&self, order_id: u64) -> Result<OrderInfo> {
        let orders = self.active_orders.read().await;

        orders
            .get(&order_id)
            .cloned()
            .ok_or_else(|| anyhow::anyhow!("Order {} not found", order_id))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_mock_executor() -> OrderExecutor {
        let rest_client = Arc::new(BinanceRestClient::new(
            "test_key".to_string(),
            "test_secret".to_string(),
            true,
        ));
        OrderExecutor::new(rest_client)
    }

    #[tokio::test]
    async fn test_execute_order_market() {
        let executor = create_mock_executor();

        let result = executor
            .execute_order("BTCUSDT", OrderSide::Buy, 0.1, OrderType::Market)
            .await
            .unwrap();

        assert!(result.success);
        assert_eq!(result.symbol, "BTCUSDT");
        assert_eq!(result.executed_qty, 0.1);
        assert!(result.execution_time_ms < 100);
    }

    #[tokio::test]
    async fn test_execute_order_limit() {
        let executor = create_mock_executor();

        let result = executor
            .execute_order(
                "ETHUSDT",
                OrderSide::Sell,
                1.0,
                OrderType::Limit { price: 3000.0 },
            )
            .await
            .unwrap();

        assert!(result.success);
        assert_eq!(result.executed_qty, 1.0);
    }

    #[tokio::test]
    async fn test_triangular_arbitrage() {
        let executor = create_mock_executor();

        let path = vec![
            "BTCUSDT".to_string(),
            "ETHBTC".to_string(),
            "ETHUSDT".to_string(),
        ];

        let result = executor
            .execute_triangular_arbitrage(path.clone(), 1000.0)
            .await
            .unwrap();

        assert_eq!(result.path, path);
        assert_eq!(result.initial_amount, 1000.0);
        assert_eq!(result.orders.len(), 3);
        assert!(result.execution_time_ms < 200);
    }

    #[tokio::test]
    async fn test_execute_batch() {
        let executor = create_mock_executor();

        let orders = vec![
            OrderRequest {
                symbol: "BTCUSDT".to_string(),
                side: OrderSide::Buy,
                quantity: 0.1,
                order_type: OrderType::Market,
            },
            OrderRequest {
                symbol: "ETHUSDT".to_string(),
                side: OrderSide::Sell,
                quantity: 1.0,
                order_type: OrderType::Market,
            },
        ];

        let results = executor.execute_batch(orders).await.unwrap();

        assert_eq!(results.len(), 2);
        assert!(results[0].success);
        assert!(results[1].success);
    }

    #[tokio::test]
    async fn test_get_order_status() {
        let executor = create_mock_executor();

        // 执行一个订单
        let result = executor
            .execute_order("BTCUSDT", OrderSide::Buy, 0.1, OrderType::Market)
            .await
            .unwrap();

        // 查询订单状态
        let order_info = executor.get_order_status(result.order_id).await.unwrap();

        assert_eq!(order_info.order_id, result.order_id);
        assert_eq!(order_info.symbol, "BTCUSDT");
        assert_eq!(order_info.status, "FILLED");
    }

    #[tokio::test]
    async fn test_cancel_all() {
        let executor = create_mock_executor();

        // 执行多个订单
        executor
            .execute_order("BTCUSDT", OrderSide::Buy, 0.1, OrderType::Market)
            .await
            .unwrap();
        executor
            .execute_order("ETHUSDT", OrderSide::Sell, 1.0, OrderType::Market)
            .await
            .unwrap();

        // 取消所有订单
        let count = executor.cancel_all().await.unwrap();

        assert_eq!(count, 2);

        // 验证活跃订单列表已清空
        let orders = executor.active_orders.read().await;
        assert_eq!(orders.len(), 0);
    }

    #[tokio::test]
    async fn test_execution_time() {
        let executor = create_mock_executor();

        let start = Instant::now();
        let result = executor
            .execute_order("BTCUSDT", OrderSide::Buy, 0.1, OrderType::Market)
            .await
            .unwrap();
        let elapsed = start.elapsed();

        assert!(result.execution_time_ms < 100);
        assert!(elapsed.as_millis() < 100);
    }
}

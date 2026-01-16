// Binance REST API 客户端
// 实现所有核心 REST API 端点

use crate::binance::types::*;
use hmac::{Hmac, Mac};
use reqwest::{Client, Response, StatusCode};
use sha2::Sha256;
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};

type HmacSha256 = Hmac<Sha256>;

/// Binance REST API 客户端
pub struct BinanceRestClient {
    api_key: String,
    api_secret: String,
    client: Client,
    base_url: String,
}

impl BinanceRestClient {
    /// 创建新的客户端实例
    ///
    /// # Arguments
    /// * `api_key` - Binance API Key
    /// * `api_secret` - Binance API Secret
    /// * `testnet` - 是否使用测试网
    pub fn new(api_key: String, api_secret: String, testnet: bool) -> Self {
        let base_url = if testnet {
            "https://testnet.binance.vision".to_string()
        } else {
            "https://api.binance.com".to_string()
        };

        Self {
            api_key,
            api_secret,
            client: Client::new(),
            base_url,
        }
    }

    /// 生成 HMAC-SHA256 签名
    fn sign(&self, query_string: &str) -> String {
        let mut mac = HmacSha256::new_from_slice(self.api_secret.as_bytes())
            .expect("HMAC can take key of any size");
        mac.update(query_string.as_bytes());
        let result = mac.finalize();
        hex::encode(result.into_bytes())
    }

    /// 获取当前时间戳（毫秒）
    fn get_timestamp() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards")
            .as_millis() as u64
    }

    /// 构建查询字符串
    fn build_query_string(params: &HashMap<String, String>) -> String {
        let mut parts: Vec<String> = params
            .iter()
            .map(|(k, v)| format!("{}={}", k, v))
            .collect();
        parts.sort(); // 确保一致的顺序
        parts.join("&")
    }

    /// 发送签名请求
    async fn signed_request<T: serde::de::DeserializeOwned>(
        &self,
        method: reqwest::Method,
        endpoint: &str,
        params: HashMap<String, String>,
    ) -> Result<T> {
        let mut params = params;
        params.insert("timestamp".to_string(), Self::get_timestamp().to_string());

        let query_string = Self::build_query_string(&params);
        let signature = self.sign(&query_string);
        let url = format!("{}{}?{}&signature={}", self.base_url, endpoint, query_string, signature);

        let response = self
            .client
            .request(method, &url)
            .header("X-MBX-APIKEY", &self.api_key)
            .send()
            .await?;

        self.handle_response(response).await
    }

    /// 发送公开请求（无需签名）
    async fn public_request<T: serde::de::DeserializeOwned>(
        &self,
        method: reqwest::Method,
        endpoint: &str,
        params: HashMap<String, String>,
    ) -> Result<T> {
        let query_string = Self::build_query_string(&params);
        let url = if query_string.is_empty() {
            format!("{}{}", self.base_url, endpoint)
        } else {
            format!("{}{}?{}", self.base_url, endpoint, query_string)
        };

        let response = self.client.request(method, &url).send().await?;
        self.handle_response(response).await
    }

    /// 处理响应
    async fn handle_response<T: serde::de::DeserializeOwned>(&self, response: Response) -> Result<T> {
        let status = response.status();

        // 检查速率限制
        if status == StatusCode::TOO_MANY_REQUESTS {
            return Err(BinanceError::RateLimitExceeded);
        }

        // 读取响应体
        let text = response.text().await?;

        if !status.is_success() {
            // 尝试解析错误消息
            if let Ok(error_msg) = serde_json::from_str::<ErrorMessage>(&text) {
                return Err(BinanceError::RequestFailed(format!(
                    "Code {}: {}",
                    error_msg.code, error_msg.msg
                )));
            }
            return Err(BinanceError::RequestFailed(format!(
                "HTTP {}: {}",
                status, text
            )));
        }

        // 解析成功响应
        serde_json::from_str(&text).map_err(|e| {
            BinanceError::ParseError(format!("Failed to parse response: {}. Body: {}", e, text))
        })
    }

    /// 获取账户信息
    ///
    /// # Returns
    /// 返回账户信息，包含所有余额
    pub async fn get_account_info(&self) -> Result<AccountInfo> {
        self.signed_request(
            reqwest::Method::GET,
            "/api/v3/account",
            HashMap::new(),
        )
        .await
    }

    /// 获取交易对信息
    ///
    /// # Returns
    /// 返回所有交易对的信息
    pub async fn get_exchange_info(&self) -> Result<ExchangeInfo> {
        self.public_request(
            reqwest::Method::GET,
            "/api/v3/exchangeInfo",
            HashMap::new(),
        )
        .await
    }

    /// 下市价单
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号，如 "BTCUSDT"
    /// * `side` - 买卖方向
    /// * `quantity` - 数量
    ///
    /// # Returns
    /// 返回订单响应
    pub async fn place_market_order(
        &self,
        symbol: &str,
        side: OrderSide,
        quantity: f64,
    ) -> Result<OrderResponse> {
        let mut params = HashMap::new();
        params.insert("symbol".to_string(), symbol.to_uppercase());
        params.insert("side".to_string(), side.to_string());
        params.insert("type".to_string(), "MARKET".to_string());
        params.insert("quantity".to_string(), format!("{:.8}", quantity));

        self.signed_request(reqwest::Method::POST, "/api/v3/order", params)
            .await
    }

    /// 下限价单
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号
    /// * `side` - 买卖方向
    /// * `quantity` - 数量
    /// * `price` - 价格
    ///
    /// # Returns
    /// 返回订单响应
    pub async fn place_limit_order(
        &self,
        symbol: &str,
        side: OrderSide,
        quantity: f64,
        price: f64,
    ) -> Result<OrderResponse> {
        let mut params = HashMap::new();
        params.insert("symbol".to_string(), symbol.to_uppercase());
        params.insert("side".to_string(), side.to_string());
        params.insert("type".to_string(), "LIMIT".to_string());
        params.insert("timeInForce".to_string(), "GTC".to_string());
        params.insert("quantity".to_string(), format!("{:.8}", quantity));
        params.insert("price".to_string(), format!("{:.8}", price));

        self.signed_request(reqwest::Method::POST, "/api/v3/order", params)
            .await
    }

    /// 查询订单状态
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号
    /// * `order_id` - 订单 ID
    ///
    /// # Returns
    /// 返回订单状态
    pub async fn get_order(&self, symbol: &str, order_id: u64) -> Result<OrderStatus> {
        let mut params = HashMap::new();
        params.insert("symbol".to_string(), symbol.to_uppercase());
        params.insert("orderId".to_string(), order_id.to_string());

        self.signed_request(reqwest::Method::GET, "/api/v3/order", params)
            .await
    }

    /// 取消订单
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号
    /// * `order_id` - 订单 ID
    ///
    /// # Returns
    /// 返回取消订单响应
    pub async fn cancel_order(&self, symbol: &str, order_id: u64) -> Result<CancelResponse> {
        let mut params = HashMap::new();
        params.insert("symbol".to_string(), symbol.to_uppercase());
        params.insert("orderId".to_string(), order_id.to_string());

        self.signed_request(reqwest::Method::DELETE, "/api/v3/order", params)
            .await
    }

    /// 获取当前价格
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号
    ///
    /// # Returns
    /// 返回当前价格
    pub async fn get_ticker_price(&self, symbol: &str) -> Result<f64> {
        let mut params = HashMap::new();
        params.insert("symbol".to_string(), symbol.to_uppercase());

        let ticker: TickerPrice = self
            .public_request(reqwest::Method::GET, "/api/v3/ticker/price", params)
            .await?;

        Ok(ticker.price)
    }

    /// 测试连接
    ///
    /// # Returns
    /// 如果连接成功返回 Ok(())
    pub async fn ping(&self) -> Result<()> {
        let _: serde_json::Value = self
            .public_request(reqwest::Method::GET, "/api/v3/ping", HashMap::new())
            .await?;
        Ok(())
    }

    /// 获取服务器时间
    ///
    /// # Returns
    /// 返回服务器时间戳（毫秒）
    pub async fn get_server_time(&self) -> Result<u64> {
        #[derive(serde::Deserialize)]
        struct ServerTime {
            #[serde(rename = "serverTime")]
            server_time: u64,
        }

        let result: ServerTime = self
            .public_request(reqwest::Method::GET, "/api/v3/time", HashMap::new())
            .await?;

        Ok(result.server_time)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sign() {
        let client = BinanceRestClient::new(
            "test_key".to_string(),
            "test_secret".to_string(),
            true,
        );

        let query = "symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559";
        let signature = client.sign(query);

        // 签名应该是一个64字符的十六进制字符串
        assert_eq!(signature.len(), 64);
    }

    #[test]
    fn test_build_query_string() {
        let mut params = HashMap::new();
        params.insert("symbol".to_string(), "BTCUSDT".to_string());
        params.insert("side".to_string(), "BUY".to_string());
        params.insert("type".to_string(), "LIMIT".to_string());

        let query = BinanceRestClient::build_query_string(&params);

        // 应该包含所有参数
        assert!(query.contains("symbol=BTCUSDT"));
        assert!(query.contains("side=BUY"));
        assert!(query.contains("type=LIMIT"));
    }

    #[test]
    fn test_get_timestamp() {
        let ts1 = BinanceRestClient::get_timestamp();
        std::thread::sleep(std::time::Duration::from_millis(10));
        let ts2 = BinanceRestClient::get_timestamp();

        assert!(ts2 > ts1);
        assert!(ts2 - ts1 >= 10);
    }

    #[tokio::test]
    async fn test_ping() {
        let client = BinanceRestClient::new(
            "".to_string(),
            "".to_string(),
            true, // 使用测试网
        );

        // Ping 是公开端点，不需要 API 密钥
        let result = client.ping().await;

        // 注意：这个测试需要网络连接
        // 如果测试网不可用，可能会失败
        match result {
            Ok(_) => println!("Ping successful"),
            Err(e) => println!("Ping failed (expected if no network): {}", e),
        }
    }
}

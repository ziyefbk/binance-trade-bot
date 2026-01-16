// Binance API 数据类型定义

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// 订单方向
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
pub enum OrderSide {
    Buy,
    Sell,
}

impl std::fmt::Display for OrderSide {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            OrderSide::Buy => write!(f, "BUY"),
            OrderSide::Sell => write!(f, "SELL"),
        }
    }
}

/// 订单类型
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
pub enum OrderType {
    Market,
    Limit,
}

impl std::fmt::Display for OrderType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            OrderType::Market => write!(f, "MARKET"),
            OrderType::Limit => write!(f, "LIMIT"),
        }
    }
}

/// 账户信息
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AccountInfo {
    pub balances: Vec<Balance>,
    pub can_trade: bool,
    pub can_withdraw: bool,
    pub can_deposit: bool,
}

/// 余额
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Balance {
    pub asset: String,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub free: f64,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub locked: f64,
}

/// 订单响应
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OrderResponse {
    pub symbol: String,
    pub order_id: u64,
    #[serde(default)]
    pub client_order_id: String,
    pub transact_time: u64,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub price: f64,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub orig_qty: f64,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub executed_qty: f64,
    pub status: String,
}

/// 订单状态查询响应
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OrderStatus {
    pub symbol: String,
    pub order_id: u64,
    pub status: String,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub price: f64,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub executed_qty: f64,
    pub time: u64,
}

/// 取消订单响应
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CancelResponse {
    pub symbol: String,
    pub order_id: u64,
    pub status: String,
}

/// 交易对信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExchangeInfo {
    pub symbols: Vec<SymbolInfo>,
}

/// 单个交易对信息
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SymbolInfo {
    pub symbol: String,
    pub base_asset: String,
    pub quote_asset: String,
    pub status: String,
}

/// 价格信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TickerPrice {
    pub symbol: String,
    #[serde(deserialize_with = "deserialize_string_to_f64")]
    pub price: f64,
}

/// WebSocket 消息类型
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum WebSocketMessage {
    Trade(TradeData),
    Depth(DepthData),
    Kline(KlineData),
    UserData(UserDataUpdate),
    Ping,
    Pong,
    Error(ErrorMessage),
}

/// 成交数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TradeData {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: u64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "p", deserialize_with = "deserialize_string_to_f64")]
    pub price: f64,
    #[serde(rename = "q", deserialize_with = "deserialize_string_to_f64")]
    pub quantity: f64,
    #[serde(rename = "T")]
    pub time: u64,
    #[serde(rename = "m")]
    pub is_buyer_maker: bool,
}

/// 深度数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DepthData {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: u64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "b")]
    pub bids: Vec<(String, String)>,
    #[serde(rename = "a")]
    pub asks: Vec<(String, String)>,
    #[serde(rename = "U")]
    pub update_time: u64,
}

impl DepthData {
    /// 将字符串格式的深度数据转换为 f64
    pub fn to_float_depth(&self) -> (Vec<(f64, f64)>, Vec<(f64, f64)>) {
        let bids = self.bids.iter()
            .filter_map(|(p, q)| {
                let price = p.parse::<f64>().ok()?;
                let qty = q.parse::<f64>().ok()?;
                Some((price, qty))
            })
            .collect();

        let asks = self.asks.iter()
            .filter_map(|(p, q)| {
                let price = p.parse::<f64>().ok()?;
                let qty = q.parse::<f64>().ok()?;
                Some((price, qty))
            })
            .collect();

        (bids, asks)
    }
}

/// K线数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KlineData {
    #[serde(rename = "e")]
    pub event_type: String,
    #[serde(rename = "E")]
    pub event_time: u64,
    #[serde(rename = "s")]
    pub symbol: String,
    #[serde(rename = "k")]
    pub kline: KlineInfo,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KlineInfo {
    #[serde(rename = "o", deserialize_with = "deserialize_string_to_f64")]
    pub open: f64,
    #[serde(rename = "h", deserialize_with = "deserialize_string_to_f64")]
    pub high: f64,
    #[serde(rename = "l", deserialize_with = "deserialize_string_to_f64")]
    pub low: f64,
    #[serde(rename = "c", deserialize_with = "deserialize_string_to_f64")]
    pub close: f64,
    #[serde(rename = "v", deserialize_with = "deserialize_string_to_f64")]
    pub volume: f64,
    #[serde(rename = "T")]
    pub close_time: u64,
}

/// 用户数据更新
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "e")]
pub enum UserDataUpdate {
    #[serde(rename = "executionReport")]
    OrderUpdate {
        #[serde(rename = "E")]
        event_time: u64,
        #[serde(rename = "s")]
        symbol: String,
        #[serde(rename = "i")]
        order_id: u64,
        #[serde(rename = "X")]
        status: String,
        #[serde(rename = "p", deserialize_with = "deserialize_string_to_f64")]
        price: f64,
        #[serde(rename = "q", deserialize_with = "deserialize_string_to_f64")]
        quantity: f64,
    },
    #[serde(rename = "outboundAccountPosition")]
    AccountUpdate {
        #[serde(rename = "E")]
        event_time: u64,
        #[serde(rename = "B")]
        balances: Vec<BalanceUpdate>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BalanceUpdate {
    #[serde(rename = "a")]
    pub asset: String,
    #[serde(rename = "f", deserialize_with = "deserialize_string_to_f64")]
    pub free: f64,
    #[serde(rename = "l", deserialize_with = "deserialize_string_to_f64")]
    pub locked: f64,
}

/// 错误消息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorMessage {
    pub code: i32,
    pub msg: String,
}

/// WebSocket 流类型
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StreamType {
    Trade,
    Depth,
    Kline,
    UserData,
}

impl StreamType {
    pub fn to_stream_name(&self, symbol: &str) -> String {
        let symbol_lower = symbol.to_lowercase();
        match self {
            StreamType::Trade => format!("{}@trade", symbol_lower),
            StreamType::Depth => format!("{}@depth@100ms", symbol_lower),
            StreamType::Kline => format!("{}@kline_1m", symbol_lower),
            StreamType::UserData => "user_data".to_string(),
        }
    }
}

/// 币安 API 错误类型
#[derive(Error, Debug)]
pub enum BinanceError {
    #[error("API request failed: {0}")]
    RequestFailed(String),

    #[error("Rate limit exceeded (code: 429)")]
    RateLimitExceeded,

    #[error("Invalid signature")]
    InvalidSignature,

    #[error("Network error: {0}")]
    NetworkError(String),

    #[error("Parse error: {0}")]
    ParseError(String),

    #[error("WebSocket error: {0}")]
    WebSocketError(String),

    #[error("Reqwest error: {0}")]
    ReqwestError(#[from] reqwest::Error),

    #[error("JSON error: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("Invalid parameter: {0}")]
    InvalidParameter(String),
}

pub type Result<T> = std::result::Result<T, BinanceError>;

/// 自定义反序列化函数：将字符串转换为 f64
fn deserialize_string_to_f64<'de, D>(deserializer: D) -> std::result::Result<f64, D::Error>
where
    D: serde::Deserializer<'de>,
{
    use serde::de::Error;
    let s: String = Deserialize::deserialize(deserializer)?;
    s.parse::<f64>().map_err(|e| Error::custom(format!("Failed to parse '{}' as f64: {}", s, e)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_order_side_serialization() {
        let buy = OrderSide::Buy;
        assert_eq!(buy.to_string(), "BUY");

        let json = serde_json::to_string(&buy).unwrap();
        assert_eq!(json, r#""BUY""#);
    }

    #[test]
    fn test_stream_type_to_stream_name() {
        assert_eq!(StreamType::Trade.to_stream_name("BTCUSDT"), "btcusdt@trade");
        assert_eq!(StreamType::Depth.to_stream_name("ETHUSDT"), "ethusdt@depth@100ms");
        assert_eq!(StreamType::Kline.to_stream_name("BNBUSDT"), "bnbusdt@kline_1m");
    }

    #[test]
    fn test_depth_data_conversion() {
        let depth = DepthData {
            event_type: "depthUpdate".to_string(),
            event_time: 123456789,
            symbol: "BTCUSDT".to_string(),
            bids: vec![
                ("50000.00".to_string(), "1.5".to_string()),
                ("49999.00".to_string(), "2.0".to_string()),
            ],
            asks: vec![
                ("50001.00".to_string(), "1.0".to_string()),
                ("50002.00".to_string(), "1.2".to_string()),
            ],
            update_time: 123456789,
        };

        let (bids, asks) = depth.to_float_depth();
        assert_eq!(bids.len(), 2);
        assert_eq!(asks.len(), 2);
        assert_eq!(bids[0], (50000.00, 1.5));
        assert_eq!(asks[0], (50001.00, 1.0));
    }
}

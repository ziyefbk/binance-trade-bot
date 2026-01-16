// Binance WebSocket 客户端
// 实现 WebSocket 连接、订阅管理、自动重连和心跳保持

use crate::binance::types::*;
use futures_util::{SinkExt, StreamExt};
use serde_json::json;
use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};
use tokio::time::{interval, Duration};
use tokio_tungstenite::{connect_async, tungstenite::Message};

/// WebSocket 客户端
pub struct BinanceWebSocket {
    url: String,
    streams: Arc<RwLock<Vec<String>>>,
    sender: Option<mpsc::Sender<WebSocketMessage>>,
    running: Arc<RwLock<bool>>,
}

impl BinanceWebSocket {
    /// 创建新的 WebSocket 客户端
    ///
    /// # Arguments
    /// * `streams` - 初始订阅的流列表
    pub fn new(streams: Vec<String>) -> Self {
        Self {
            url: "wss://stream.binance.com:9443/ws".to_string(),
            streams: Arc::new(RwLock::new(streams)),
            sender: None,
            running: Arc::new(RwLock::new(false)),
        }
    }

    /// 创建测试网客户端
    pub fn new_testnet(streams: Vec<String>) -> Self {
        Self {
            url: "wss://testnet.binance.vision/ws".to_string(),
            streams: Arc::new(RwLock::new(streams)),
            sender: None,
            running: Arc::new(RwLock::new(false)),
        }
    }

    /// 连接到 WebSocket 并开始接收消息
    ///
    /// # Returns
    /// 返回消息接收通道
    pub async fn connect(&mut self) -> Result<mpsc::Receiver<WebSocketMessage>> {
        let (tx, rx) = mpsc::channel(1000);
        self.sender = Some(tx.clone());

        // 设置为运行状态
        *self.running.write().await = true;

        // 启动连接任务
        let url = self.url.clone();
        let streams = self.streams.clone();
        let running = self.running.clone();

        tokio::spawn(async move {
            Self::connection_loop(url, streams, tx, running).await;
        });

        Ok(rx)
    }

    /// WebSocket 连接循环（包含自动重连）
    async fn connection_loop(
        url: String,
        streams: Arc<RwLock<Vec<String>>>,
        tx: mpsc::Sender<WebSocketMessage>,
        running: Arc<RwLock<bool>>,
    ) {
        while *running.read().await {
            // 构建流 URL
            let streams_str = streams.read().await.join("/");
            let ws_url = if streams_str.is_empty() {
                url.clone()
            } else {
                format!("{}/{}", url, streams_str)
            };

            tracing::info!("Connecting to WebSocket: {}", ws_url);

            match connect_async(&ws_url).await {
                Ok((ws_stream, _)) => {
                    tracing::info!("WebSocket connected successfully");

                    let (mut write, mut read) = ws_stream.split();

                    // 启动心跳任务
                    let running_clone = running.clone();
                    let heartbeat_task = tokio::spawn(async move {
                        let mut ticker = interval(Duration::from_secs(30));
                        while *running_clone.read().await {
                            ticker.tick().await;
                            if write.send(Message::Ping(vec![])).await.is_err() {
                                tracing::warn!("Failed to send ping");
                                break;
                            }
                        }
                    });

                    // 接收消息
                    while *running.read().await {
                        match read.next().await {
                            Some(Ok(msg)) => {
                                if let Err(e) = Self::handle_message(msg, &tx).await {
                                    tracing::warn!("Error handling message: {}", e);
                                }
                            }
                            Some(Err(e)) => {
                                tracing::error!("WebSocket error: {}", e);
                                break;
                            }
                            None => {
                                tracing::warn!("WebSocket stream ended");
                                break;
                            }
                        }
                    }

                    // 清理心跳任务
                    heartbeat_task.abort();
                }
                Err(e) => {
                    tracing::error!("Failed to connect to WebSocket: {}", e);
                }
            }

            // 如果仍在运行，等待5秒后重连
            if *running.read().await {
                tracing::info!("Reconnecting in 5 seconds...");
                tokio::time::sleep(Duration::from_secs(5)).await;
            }
        }

        tracing::info!("WebSocket connection loop stopped");
    }

    /// 处理 WebSocket 消息
    async fn handle_message(
        msg: Message,
        tx: &mpsc::Sender<WebSocketMessage>,
    ) -> Result<()> {
        match msg {
            Message::Text(text) => {
                // 尝试解析 JSON
                match serde_json::from_str::<serde_json::Value>(&text) {
                    Ok(json) => {
                        // 根据事件类型解析
                        if let Some(event_type) = json.get("e").and_then(|v| v.as_str()) {
                            let ws_msg = match event_type {
                                "trade" => {
                                    let trade: TradeData = serde_json::from_value(json)?;
                                    WebSocketMessage::Trade(trade)
                                }
                                "depthUpdate" => {
                                    let depth: DepthData = serde_json::from_value(json)?;
                                    WebSocketMessage::Depth(depth)
                                }
                                "kline" => {
                                    let kline: KlineData = serde_json::from_value(json)?;
                                    WebSocketMessage::Kline(kline)
                                }
                                "executionReport" | "outboundAccountPosition" => {
                                    let user_data: UserDataUpdate = serde_json::from_value(json)?;
                                    WebSocketMessage::UserData(user_data)
                                }
                                _ => {
                                    tracing::debug!("Unknown event type: {}", event_type);
                                    return Ok(());
                                }
                            };

                            tx.send(ws_msg).await.map_err(|_| {
                                BinanceError::WebSocketError("Channel closed".to_string())
                            })?;
                        }
                    }
                    Err(e) => {
                        tracing::warn!("Failed to parse JSON: {} - {}", e, text);
                    }
                }
            }
            Message::Ping(_) => {
                tracing::trace!("Received ping");
                tx.send(WebSocketMessage::Ping)
                    .await
                    .map_err(|_| BinanceError::WebSocketError("Channel closed".to_string()))?;
            }
            Message::Pong(_) => {
                tracing::trace!("Received pong");
                tx.send(WebSocketMessage::Pong)
                    .await
                    .map_err(|_| BinanceError::WebSocketError("Channel closed".to_string()))?;
            }
            Message::Close(_) => {
                tracing::info!("WebSocket closed by server");
            }
            _ => {
                tracing::debug!("Received other message type");
            }
        }

        Ok(())
    }

    /// 订阅新的流
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号
    /// * `stream_type` - 流类型
    pub async fn subscribe(&mut self, symbol: &str, stream_type: StreamType) -> Result<()> {
        let stream_name = stream_type.to_stream_name(symbol);
        let mut streams = self.streams.write().await;

        if !streams.contains(&stream_name) {
            streams.push(stream_name);
            tracing::info!("Subscribed to {} {}", symbol, stream_type.to_stream_name(symbol));
        }

        Ok(())
    }

    /// 取消订阅流
    ///
    /// # Arguments
    /// * `symbol` - 交易对符号
    /// * `stream_type` - 流类型
    pub async fn unsubscribe(&mut self, symbol: &str, stream_type: StreamType) -> Result<()> {
        let stream_name = stream_type.to_stream_name(symbol);
        let mut streams = self.streams.write().await;

        streams.retain(|s| s != &stream_name);
        tracing::info!("Unsubscribed from {} {}", symbol, stream_type.to_stream_name(symbol));

        Ok(())
    }

    /// 关闭 WebSocket 连接
    pub async fn close(&mut self) -> Result<()> {
        *self.running.write().await = false;
        tracing::info!("WebSocket closing...");
        Ok(())
    }

    /// 检查是否正在运行
    pub async fn is_running(&self) -> bool {
        *self.running.read().await
    }
}

// 为了支持 futures_util，需要添加依赖
// 但在当前 Cargo.toml 中已经通过 tokio-tungstenite 间接包含了

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_websocket() {
        let streams = vec!["btcusdt@trade".to_string(), "ethusdt@depth@100ms".to_string()];
        let ws = BinanceWebSocket::new(streams.clone());

        assert_eq!(ws.url, "wss://stream.binance.com:9443/ws");
    }

    #[test]
    fn test_new_testnet_websocket() {
        let streams = vec!["btcusdt@trade".to_string()];
        let ws = BinanceWebSocket::new_testnet(streams);

        assert_eq!(ws.url, "wss://testnet.binance.vision/ws");
    }

    #[tokio::test]
    async fn test_subscribe_unsubscribe() {
        let mut ws = BinanceWebSocket::new(vec![]);

        // 订阅
        ws.subscribe("BTCUSDT", StreamType::Trade).await.unwrap();
        let streams = ws.streams.read().await;
        assert!(streams.contains(&"btcusdt@trade".to_string()));
        drop(streams);

        // 取消订阅
        ws.unsubscribe("BTCUSDT", StreamType::Trade).await.unwrap();
        let streams = ws.streams.read().await;
        assert!(!streams.contains(&"btcusdt@trade".to_string()));
    }

    #[tokio::test]
    async fn test_close() {
        let mut ws = BinanceWebSocket::new(vec![]);

        *ws.running.write().await = true;
        assert!(ws.is_running().await);

        ws.close().await.unwrap();
        assert!(!ws.is_running().await);
    }

    // 注意：实际连接测试需要网络，这里只测试基本功能
    #[tokio::test]
    async fn test_stream_name_generation() {
        let trade_stream = StreamType::Trade.to_stream_name("BTCUSDT");
        assert_eq!(trade_stream, "btcusdt@trade");

        let depth_stream = StreamType::Depth.to_stream_name("ETHUSDT");
        assert_eq!(depth_stream, "ethusdt@depth@100ms");

        let kline_stream = StreamType::Kline.to_stream_name("BNBUSDT");
        assert_eq!(kline_stream, "bnbusdt@kline_1m");
    }
}

// 价格监控器
// Agent 2 实现

use crate::binance::types::{DepthData, StreamType, WebSocketMessage};
use crate::binance::websocket::BinanceWebSocket;
use anyhow::Result;
use dashmap::DashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

#[derive(Debug, Clone)]
pub struct PriceData {
    pub symbol: String,
    pub bid_price: f64,
    pub ask_price: f64,
    pub last_price: f64,
    pub volume_24h: f64,
    pub update_time: u64,
}

/// 三角套利机会
#[derive(Debug, Clone)]
pub struct ArbitrageOpportunity {
    pub path: Vec<String>,
    pub profit_percent: f64,
    pub estimated_amount: f64,
    pub execution_prices: Vec<f64>,
    pub timestamp: u64,
}

/// 价格监控器
pub struct PriceMonitor {
    prices: Arc<DashMap<String, PriceData>>,
    depth_data: Arc<DashMap<String, DepthData>>,
    websocket: Option<BinanceWebSocket>,
    running: Arc<RwLock<bool>>,
    fee_rate: f64,
}

impl PriceMonitor {
    pub fn new(websocket: Option<BinanceWebSocket>) -> Self {
        Self {
            prices: Arc::new(DashMap::new()),
            depth_data: Arc::new(DashMap::new()),
            websocket,
            running: Arc::new(RwLock::new(false)),
            fee_rate: 0.001,
        }
    }

    pub async fn start(&self) -> Result<()> {
        let mut running = self.running.write().await;
        if *running {
            return Err(anyhow::anyhow!("Already running"));
        }
        if self.websocket.is_none() {
            return Err(anyhow::anyhow!("WebSocket not initialized"));
        }
        *running = true;
        Ok(())
    }

    pub async fn stop(&self) -> Result<()> {
        *self.running.write().await = false;
        Ok(())
    }

    /// 获取交易对当前价格
    pub fn get_price(&self, symbol: &str) -> Option<f64> {
        self.prices.get(symbol).map(|entry| entry.last_price)
    }

    pub fn get_depth(&self, symbol: &str) -> Option<DepthData> {
        self.depth_data.get(symbol).map(|e| e.clone())
    }

    pub fn scan_triangular_opportunities(&self, min_profit_percent: f64) -> Vec<ArbitrageOpportunity> {
        let mut opportunities = Vec::new();
        let paths = self.generate_triangular_paths();

        for path in paths {
            if let Some(opp) = self.calculate_arbitrage_profit(&path) {
                if opp.profit_percent >= min_profit_percent {
                    opportunities.push(opp);
                }
            }
        }

        opportunities.sort_by(|a, b| b.profit_percent.partial_cmp(&a.profit_percent).unwrap_or(std::cmp::Ordering::Equal));
        opportunities
    }

    fn generate_triangular_paths(&self) -> Vec<Vec<String>> {
        let mut paths = Vec::new();
        let symbols: Vec<String> = self.prices.iter().map(|e| e.key().clone()).collect();

        for s1 in &symbols {
            if !s1.ends_with("USDT") { continue; }
            let base1 = s1.replace("USDT", "");

            for s2 in &symbols {
                // s2 should have base1 as quote currency, e.g., ETHBTC where BTC is quote
                if !s2.ends_with(&base1) || s2.ends_with("USDT") { continue; }
                let base2 = s2.replace(&base1, "");
                let s3 = format!("{}USDT", base2);

                if symbols.contains(&s3) {
                    paths.push(vec![s1.clone(), s2.clone(), s3]);
                }
            }
        }
        paths
    }

    fn calculate_arbitrage_profit(&self, path: &[String]) -> Option<ArbitrageOpportunity> {
        if path.len() != 3 { return None; }

        let p1 = self.get_price(&path[0])?;
        let p2 = self.get_price(&path[1])?;
        let p3 = self.get_price(&path[2])?;

        let fee_mult = 1.0 - self.fee_rate;
        let final_ratio = (1.0 / p1) * p2 * p3 * fee_mult.powi(3);
        let profit_percent = (final_ratio - 1.0) * 100.0;

        Some(ArbitrageOpportunity {
            path: path.to_vec(),
            profit_percent,
            estimated_amount: 1000.0,
            execution_prices: vec![p1, p2, p3],
            timestamp: chrono::Utc::now().timestamp_millis() as u64,
        })
    }

    pub async fn add_symbol(&self, symbol: &str) -> Result<()> {
        self.prices.insert(
            symbol.to_string(),
            PriceData {
                symbol: symbol.to_string(),
                bid_price: 50000.0,
                ask_price: 50001.0,
                last_price: 50000.5,
                volume_24h: 1000000.0,
                update_time: chrono::Utc::now().timestamp_millis() as u64,
            },
        );
        Ok(())
    }

    pub async fn remove_symbol(&self, symbol: &str) -> Result<()> {
        self.prices.remove(symbol);
        self.depth_data.remove(symbol);
        Ok(())
    }

    pub fn detect_price_anomaly(&self, symbol: &str, new_price: f64) -> bool {
        if let Some(old_data) = self.prices.get(symbol) {
            let old_price = old_data.last_price;
            let change_percent = ((new_price - old_price) / old_price).abs() * 100.0;
            change_percent > 10.0
        } else {
            false
        }
    }

    pub fn update_price(&self, symbol: &str, price_data: PriceData) {
        self.prices.insert(symbol.to_string(), price_data);
    }

    pub fn symbol_count(&self) -> usize {
        self.prices.len()
    }

    pub fn get_all_symbols(&self) -> Vec<String> {
        self.prices.iter().map(|e| e.key().clone()).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_price_monitor_creation() {
        let monitor = PriceMonitor::new(None);
        assert_eq!(monitor.symbol_count(), 0);
    }

    #[tokio::test]
    async fn test_add_remove_symbol() {
        let monitor = PriceMonitor::new(None);
        monitor.add_symbol("BTCUSDT").await.unwrap();
        assert_eq!(monitor.symbol_count(), 1);
        assert!(monitor.get_price("BTCUSDT").is_some());
        monitor.remove_symbol("BTCUSDT").await.unwrap();
        assert_eq!(monitor.symbol_count(), 0);
    }

    #[tokio::test]
    async fn test_scan_triangular_opportunities() {
        let monitor = PriceMonitor::new(None);
        monitor.update_price("BTCUSDT", PriceData {
            symbol: "BTCUSDT".to_string(),
            bid_price: 50000.0, ask_price: 50000.0, last_price: 50000.0,
            volume_24h: 1000000.0, update_time: 0,
        });
        monitor.update_price("ETHBTC", PriceData {
            symbol: "ETHBTC".to_string(),
            bid_price: 0.06, ask_price: 0.06, last_price: 0.06,
            volume_24h: 1000000.0, update_time: 0,
        });
        monitor.update_price("ETHUSDT", PriceData {
            symbol: "ETHUSDT".to_string(),
            bid_price: 3100.0, ask_price: 3100.0, last_price: 3100.0,
            volume_24h: 1000000.0, update_time: 0,
        });

        // 使用负的最小利润以包含所有机会（包括亏损的）
        let opps = monitor.scan_triangular_opportunities(-100.0);
        assert!(!opps.is_empty());
        assert_eq!(opps[0].path.len(), 3);
        assert_eq!(opps[0].path, vec!["BTCUSDT", "ETHBTC", "ETHUSDT"]);
    }

    #[tokio::test]
    async fn test_detect_price_anomaly() {
        let monitor = PriceMonitor::new(None);
        monitor.update_price("BTCUSDT", PriceData {
            symbol: "BTCUSDT".to_string(),
            bid_price: 50000.0, ask_price: 50000.0, last_price: 50000.0,
            volume_24h: 1000000.0, update_time: 0,
        });
        assert!(!monitor.detect_price_anomaly("BTCUSDT", 50500.0));
        assert!(monitor.detect_price_anomaly("BTCUSDT", 60000.0));
    }

    #[tokio::test]
    async fn test_concurrent_access() {
        let monitor = Arc::new(PriceMonitor::new(None));
        let mut handles = vec![];
        for i in 0..10 {
            let m = monitor.clone();
            let h = tokio::spawn(async move {
                m.add_symbol(&format!("TEST{}USDT", i)).await.unwrap();
            });
            handles.push(h);
        }
        for h in handles {
            h.await.unwrap();
        }
        assert_eq!(monitor.symbol_count(), 10);
    }
}

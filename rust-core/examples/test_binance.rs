// 测试 binance 模块的基本功能
// 运行: cargo run --example test_binance

#[path = "../src/binance/mod.rs"]
mod binance;

use binance::types::*;

fn main() {
    println!("=== Testing Binance Types ===");
    
    // 测试订单方向
    let buy = OrderSide::Buy;
    let sell = OrderSide::Sell;
    println!("OrderSide::Buy => {}", buy);
    println!("OrderSide::Sell => {}", sell);
    
    // 测试订单类型  
    let market = OrderType::Market;
    let limit = OrderType::Limit;
    println!("OrderType::Market => {}", market);
    println!("OrderType::Limit => {}", limit);
    
    // 测试流类型
    let trade_stream = StreamType::Trade.to_stream_name("BTCUSDT");
    let depth_stream = StreamType::Depth.to_stream_name("ETHUSDT");
    let kline_stream = StreamType::Kline.to_stream_name("BNBUSDT");
    
    println!("\nStream names:");
    println!("  Trade: {}", trade_stream);
    println!("  Depth: {}", depth_stream);
    println!("  Kline: {}", kline_stream);
    
    println!("\n✅ All tests passed!");
}

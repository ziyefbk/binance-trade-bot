#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <unordered_map>
#include <optional>
#include <chrono>

namespace binance {

// ============================================================================
// ENUMS
// ============================================================================

enum class OrderSide : uint8_t {
    Buy,
    Sell
};

enum class OrderType : uint8_t {
    Market,
    Limit,
    StopLoss
};

enum class OrderStatus : uint8_t {
    New,
    PartiallyFilled,
    Filled,
    Cancelled,
    Rejected,
    Expired
};

// ============================================================================
// BASIC TYPES
// ============================================================================

/// Account balance for a single asset
struct Balance {
    std::string asset;      ///< Asset name (e.g., "BTC", "USDT")
    double free = 0.0;      ///< Available balance
    double locked = 0.0;    ///< Locked in orders

    /// Total balance = free + locked
    double total() const {
        return free + locked;
    }
};

/// Account information
struct AccountInfo {
    int64_t maker_commission = 0;
    int64_t taker_commission = 0;
    int64_t buyer_commission = 0;
    int64_t seller_commission = 0;
    bool can_trade = true;
    bool can_deposit = true;
    bool can_withdraw = true;
    int64_t update_time = 0;
    std::vector<Balance> balances;
};

// ============================================================================
// ORDER & EXECUTION TYPES
// ============================================================================

/// Order request parameters
struct OrderRequest {
    std::string symbol;           ///< Trading pair (e.g., "BTCUSDT")
    OrderSide side = OrderSide::Buy;
    double quantity = 0.0;        ///< Amount to trade
    OrderType type = OrderType::Market;
    std::optional<double> price;  ///< Price for limit orders
    int64_t timestamp = 0;        ///< Request timestamp (nanoseconds)
};

/// Result of a single order execution
struct OrderResult {
    bool success = false;
    std::string error_message;
    uint64_t order_id = 0;
    std::string symbol;
    OrderSide side = OrderSide::Buy;
    double avg_price = 0.0;       ///< Average execution price
    double executed_qty = 0.0;    ///< Executed quantity
    int64_t executed_time = 0;    ///< Execution timestamp (nanoseconds)
};

/// Result of complete arbitrage execution
struct ExecutionResult {
    bool success = false;
    std::string error_message;

    // Order information
    std::vector<uint64_t> order_ids;
    std::vector<OrderResult> orders;

    // Profitability
    double initial_amount = 0.0;
    double final_amount = 0.0;
    double profit_usdt = 0.0;
    double profit_percent = 0.0;
    double actual_fee_percent = 0.0;

    // Performance
    int64_t execution_time_ns = 0;  ///< Total execution time in nanoseconds

    // Price details
    std::vector<double> execution_prices;

    // Timestamp
    int64_t completed_time = 0;
};

// ============================================================================
// PRICE & MARKET DATA TYPES
// ============================================================================

/// Price data for a trading pair
struct PriceData {
    std::string symbol;
    double bid = 0.0;
    double ask = 0.0;
    double last = 0.0;
    double high_24h = 0.0;
    double low_24h = 0.0;
    double volume_24h = 0.0;
    int64_t timestamp = 0;  ///< Update timestamp (nanoseconds)
};

/// Order book depth data
struct DepthData {
    std::string symbol;
    std::vector<std::pair<double, double>> bids;    ///< {price, quantity}
    std::vector<std::pair<double, double>> asks;    ///< {price, quantity}
    int64_t timestamp = 0;
};

/// Trade information
struct Trade {
    std::string symbol;
    uint64_t trade_id = 0;
    double price = 0.0;
    double quantity = 0.0;
    OrderSide side = OrderSide::Buy;
    int64_t timestamp = 0;
};

// ============================================================================
// ARBITRAGE TYPES
// ============================================================================

/// A single arbitrage opportunity
struct ArbitrageOpportunity {
    std::vector<std::string> path;           ///< Trading pair path (e.g., ["BTCUSDT", "ETHBTC", "ETHUSDT"])
    double profit_percent = 0.0;             ///< Expected profit percentage
    double estimated_amount = 0.0;           ///< Available liquidity in first pair
    std::vector<double> execution_prices;    ///< Price for each leg
    int64_t timestamp = 0;                   ///< Detection timestamp (nanoseconds)

    /// Validate that this is a valid triangular path
    bool is_valid() const {
        return path.size() == 3 && profit_percent > 0.0 && estimated_amount > 0.0;
    }

    /// Check if profit exceeds threshold
    bool meets_threshold(double threshold) const {
        return profit_percent >= threshold;
    }
};

// ============================================================================
// RATE LIMITER TYPES
// ============================================================================

/// Rate limiting statistics
struct RateLimitStats {
    double available_tokens = 0.0;
    double total_tokens = 0.0;
    double refill_rate = 0.0;      ///< Tokens per second
    int64_t last_refill_time = 0;
};

// ============================================================================
// CONFIGURATION TYPES
// ============================================================================

/// API configuration
struct APIConfig {
    std::string api_key;
    std::string api_secret;
    bool testnet = true;
    std::string rest_endpoint = "https://testnet.binance.vision";
    std::string websocket_endpoint = "wss://stream.testnet.binance.vision:9443";
};

/// Performance configuration
struct PerformanceConfig {
    int64_t websocket_timeout_ms = 30000;      ///< 30 seconds
    int64_t rest_request_timeout_ms = 10000;   ///< 10 seconds
    int max_concurrent_orders = 10;
    int order_executor_threads = 4;
};

/// Trading configuration
struct TradingConfig {
    double min_profit_percent = 0.1;           ///< Minimum profitable percentage
    double max_position_usdt = 1000.0;         ///< Maximum single position
    double slippage_tolerance = 0.5;           ///< Maximum price change tolerance (%)
    std::vector<std::string> trading_pairs;    ///< Pairs to monitor
};

// ============================================================================
// TIME UTILITIES
// ============================================================================

/// Get current time in nanoseconds
inline int64_t get_time_ns() {
    using namespace std::chrono;
    return duration_cast<nanoseconds>(high_resolution_clock::now().time_since_epoch()).count();
}

/// Get current time in milliseconds
inline int64_t get_time_ms() {
    return get_time_ns() / 1000000;
}

/// Get current time in microseconds
inline int64_t get_time_us() {
    return get_time_ns() / 1000;
}

} // namespace binance

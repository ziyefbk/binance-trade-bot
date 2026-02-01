#pragma once

#include <string>
#include <vector>

namespace binance {

// ============================================================================
// API ENDPOINTS
// ============================================================================

constexpr const char* REST_API_BASE_TESTNET = "https://testnet.binance.vision/api";
constexpr const char* REST_API_BASE_MAINNET = "https://api.binance.com/api";

constexpr const char* WEBSOCKET_BASE_TESTNET = "wss://stream.testnet.binance.vision:9443/ws";
constexpr const char* WEBSOCKET_BASE_MAINNET = "wss://stream.binance.com:9443/ws";

// REST API Endpoints
constexpr const char* ENDPOINT_ACCOUNT_INFO = "/v3/account";
constexpr const char* ENDPOINT_ORDER = "/v3/order";
constexpr const char* ENDPOINT_TICKER = "/v3/ticker/price";
constexpr const char* ENDPOINT_DEPTH = "/v3/depth";
constexpr const char* ENDPOINT_RECENT_TRADES = "/v3/trades";

// ============================================================================
// EXCHANGE RATES & FEES
// ============================================================================

/// Standard Binance trading fee (0.1%)
constexpr double DEFAULT_TRADING_FEE = 0.001;

/// Maker fee (0.1%)
constexpr double MAKER_FEE = 0.001;

/// Taker fee (0.1%)
constexpr double TAKER_FEE = 0.001;

// ============================================================================
// RATE LIMITING
// ============================================================================

/// Binance rate limit: 1200 requests per minute
constexpr int64_t RATE_LIMIT_PER_MINUTE = 1200;

/// Binance rate limit: 50 orders per 10 seconds
constexpr int64_t RATE_LIMIT_ORDERS_PER_10_SEC = 50;

/// Binance rate limit: 160,000 orders per 24 hours
constexpr int64_t RATE_LIMIT_ORDERS_PER_DAY = 160000;

/// Default tokens to acquire per request
constexpr double DEFAULT_REQUEST_TOKENS = 1.0;

/// Default tokens to acquire for order placement
constexpr double ORDER_PLACEMENT_TOKENS = 1.0;

// ============================================================================
// TRADING PARAMETERS
// ============================================================================

/// Minimum order quantity (in base currency)
constexpr double MIN_ORDER_QUANTITY = 0.00001;

/// Maximum order quantity
constexpr double MAX_ORDER_QUANTITY = 10000.0;

/// Default price precision (decimal places)
constexpr int DEFAULT_PRICE_PRECISION = 8;

/// Default quantity precision (decimal places)
constexpr int DEFAULT_QUANTITY_PRECISION = 8;

// ============================================================================
// TIMEOUTS & RETRIES
// ============================================================================

/// WebSocket connection timeout (milliseconds)
constexpr int64_t WEBSOCKET_CONNECT_TIMEOUT_MS = 10000;

/// WebSocket read timeout (milliseconds)
constexpr int64_t WEBSOCKET_READ_TIMEOUT_MS = 30000;

/// REST API request timeout (milliseconds)
constexpr int64_t REST_REQUEST_TIMEOUT_MS = 10000;

/// Reconnection base delay (milliseconds)
constexpr int64_t RECONNECT_BASE_DELAY_MS = 1000;

/// Reconnection max delay (milliseconds)
constexpr int64_t RECONNECT_MAX_DELAY_MS = 60000;

/// Maximum reconnection attempts before giving up
constexpr int MAX_RECONNECT_ATTEMPTS = 100;

// ============================================================================
// PERFORMANCE TARGETS
// ============================================================================

/// WebSocket message processing target (microseconds)
constexpr int64_t TARGET_WEBSOCKET_LATENCY_US = 100;

/// Price monitor read/write target (microseconds)
constexpr int64_t TARGET_PRICE_MONITOR_LATENCY_US = 1;

/// Order execution target (microseconds)
constexpr int64_t TARGET_ORDER_EXECUTION_US = 500;

/// Triangular arbitrage execution target (microseconds)
constexpr int64_t TARGET_ARBITRAGE_EXECUTION_US = 1000;

// ============================================================================
// LOGGING LEVELS
// ============================================================================

enum class LogLevel : uint8_t {
    Debug = 0,
    Info = 1,
    Warning = 2,
    Error = 3,
    Critical = 4
};

// ============================================================================
// COMMON TRADING PAIRS
// ============================================================================

const std::vector<std::string> MAJOR_TRADING_PAIRS = {
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "ADAUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "MATICUSDT",
    "AVAXUSDT",
    "FTMUSDT",
};

const std::vector<std::string> BINANCE_TRADING_PAIRS = {
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "ETHBTC",
    "BNBBTC",
    "BNBETH",
};

} // namespace binance

#pragma once

#include "binance/rest_client.h"
#include "binance/websocket_client.h"
#include "core/price_monitor.h"
#include "core/rate_limiter.h"
#include "core/order_executor.h"
#include <string>
#include <vector>
#include <memory>

namespace binance {

/// Main Binance trading engine
///
/// Orchestrates all components: REST API, WebSocket, price monitoring, order execution
/// This is the primary interface exposed to Python via Pybind11
class BinanceEngine {
public:
    /// Constructor
    /// @param api_key Binance API key
    /// @param api_secret Binance API secret
    /// @param testnet Whether to use testnet (default: true)
    BinanceEngine(const std::string& api_key,
                  const std::string& api_secret,
                  bool testnet = true);

    /// Start market data collection
    void start_market_data(const std::vector<std::string>& symbols);

    /// Stop market data collection
    void stop_market_data();

    /// Get current price for a symbol
    double get_price(const std::string& symbol) const;

    /// Scan for arbitrage opportunities
    std::vector<ArbitrageOpportunity> get_arbitrage_opportunities(double min_profit_percent);

    /// Execute triangular arbitrage
    ExecutionResult execute_triangular_arbitrage(const std::vector<std::string>& path,
                                                  double amount);

    /// Get account balances
    std::vector<Balance> get_balances();

    /// Place market order
    OrderResult place_order(const std::string& symbol,
                           const std::string& side,
                           double quantity);

private:
    std::unique_ptr<RestClient> rest_client_;
    std::unique_ptr<BinanceWebSocketClient> websocket_client_;
    std::unique_ptr<PriceMonitor> price_monitor_;
    std::unique_ptr<RateLimiter> rate_limiter_;
    std::unique_ptr<OrderExecutor> order_executor_;

    bool testnet_;
};

} // namespace binance

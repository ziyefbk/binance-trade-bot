#pragma once

#include "binance/rest_client.h"
#include "rate_limiter.h"
#include "binance/types.h"
#include <string>
#include <vector>
#include <memory>

namespace binance {

/// Executes orders and arbitrage trades
class OrderExecutor {
public:
    OrderExecutor(RestClient* rest_client, RateLimiter* rate_limiter);

    /// Execute single order
    OrderResult execute_order(const std::string& symbol,
                             const std::string& side,
                             double quantity);

    /// Execute triangular arbitrage (3 orders)
    ExecutionResult execute_triangular_arbitrage(const std::vector<std::string>& path,
                                                 double amount);

private:
    RestClient* rest_client_;
    RateLimiter* rate_limiter_;
};

} // namespace binance

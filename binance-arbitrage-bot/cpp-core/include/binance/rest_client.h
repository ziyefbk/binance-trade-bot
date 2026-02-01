#pragma once

#include "types.h"
#include <string>
#include <vector>
#include <optional>

namespace binance {

/// Binance REST API client
///
/// Handles HTTP communication with Binance API
/// - Request signing with HMAC-SHA256
/// - Rate limiting
/// - Error handling and retries
class BinanceRestClient {
public:
    BinanceRestClient(std::string api_key, std::string api_secret, bool testnet = true);

    /// Get account information
    AccountInfo get_account_info();

    /// Place market order
    OrderResult place_market_order(const std::string& symbol,
                                   const std::string& side,
                                   double quantity);

    /// Get current ticker price
    double get_ticker_price(const std::string& symbol);

    /// Get order book depth
    // DepthData get_depth(const std::string& symbol, int limit = 20);

private:
    std::string api_key_;
    std::string api_secret_;
    bool testnet_;
};

// Convenience alias
using RestClient = BinanceRestClient;

} // namespace binance

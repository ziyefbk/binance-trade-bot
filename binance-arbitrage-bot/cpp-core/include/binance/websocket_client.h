#pragma once

#include "types.h"
#include <string>
#include <vector>
#include <functional>

namespace binance {

/// Binance WebSocket client
///
/// Handles WebSocket connections for real-time market data
/// - Automatic reconnection
/// - Message parsing
/// - Multiple stream subscriptions
class BinanceWebSocketClient {
public:
    BinanceWebSocketClient(std::string api_key, std::string api_secret);

    /// Connect to WebSocket
    void connect();

    /// Subscribe to ticker stream for a symbol
    void subscribe(const std::string& symbol);

    /// Set message callback
    void on_message(std::function<void(const std::string&)> callback);

    /// Disconnect from WebSocket
    void disconnect();

    /// Check if connected
    bool is_connected() const;

private:
    std::string api_key_;
    std::string api_secret_;
};

} // namespace binance

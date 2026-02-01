#include "binance/websocket_client.h"

namespace binance {

// WebSocket client placeholder
// Full implementation in Phase 4

BinanceWebSocketClient::BinanceWebSocketClient(std::string api_key, std::string api_secret)
    : api_key_(std::move(api_key)),
      api_secret_(std::move(api_secret)) {
}

} // namespace binance

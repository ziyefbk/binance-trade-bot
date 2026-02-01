#include "binance/engine.h"

namespace binance {

// Binance Engine placeholder
// Full implementation in Phase 6

BinanceEngine::BinanceEngine(const std::string& api_key,
                             const std::string& api_secret,
                             bool testnet)
    : rest_client_(api_key, api_secret, testnet),
      websocket_client_(api_key, api_secret),
      testnet_(testnet) {
}

} // namespace binance

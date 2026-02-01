#include "binance/rest_client.h"

namespace binance {

// REST API client placeholder
// Full implementation in Phase 3

BinanceRestClient::BinanceRestClient(std::string api_key, std::string api_secret, bool testnet)
    : api_key_(std::move(api_key)),
      api_secret_(std::move(api_secret)),
      testnet_(testnet) {
}

} // namespace binance

#include "core/order_executor.h"

namespace binance {

// Order executor placeholder
// Full implementation in Phase 5

OrderExecutor::OrderExecutor(RestClient* rest_client, RateLimiter* rate_limiter)
    : rest_client_(rest_client), rate_limiter_(rate_limiter) {
}

} // namespace binance

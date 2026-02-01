#include "core/rate_limiter.h"

namespace binance {

// Rate limiter placeholder
// Full implementation in Phase 2

RateLimiter::RateLimiter(double max_tokens, double refill_rate)
    : max_tokens_(max_tokens),
      tokens_(max_tokens),
      refill_rate_(refill_rate) {
}

} // namespace binance

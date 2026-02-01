#pragma once

#include "types.h"
#include <atomic>
#include <chrono>
#include <cstdint>

namespace binance {

/// Token bucket rate limiter
///
/// Implements the token bucket algorithm for rate limiting
/// - Non-blocking token acquisition
/// - Automatic token refill
/// - Thread-safe using atomics
class RateLimiter {
public:
    /// Constructor
    /// @param max_tokens Maximum number of tokens in bucket
    /// @param refill_rate Tokens added per second
    RateLimiter(double max_tokens, double refill_rate);

    /// Try to acquire tokens (non-blocking)
    bool try_acquire(double tokens = 1.0);

    /// Get available tokens
    double available_tokens();

private:
    double max_tokens_;
    std::atomic<double> tokens_;
    double refill_rate_;
    std::chrono::high_resolution_clock::time_point last_refill_;
};

} // namespace binance

#pragma once

#include <chrono>
#include <cstdint>

namespace binance {

/// High-resolution timer for performance measurement
class Timer {
public:
    Timer() : start_(std::chrono::high_resolution_clock::now()) {}

    /// Restart the timer
    void reset() {
        start_ = std::chrono::high_resolution_clock::now();
    }

    /// Get elapsed time in nanoseconds
    int64_t elapsed_ns() const {
        auto now = std::chrono::high_resolution_clock::now();
        return std::chrono::duration_cast<std::chrono::nanoseconds>(now - start_).count();
    }

    /// Get elapsed time in microseconds
    int64_t elapsed_us() const {
        return elapsed_ns() / 1000;
    }

    /// Get elapsed time in milliseconds
    int64_t elapsed_ms() const {
        return elapsed_ns() / 1000000;
    }

    /// Get elapsed time in seconds
    double elapsed_s() const {
        return static_cast<double>(elapsed_ns()) / 1e9;
    }

private:
    std::chrono::high_resolution_clock::time_point start_;
};

} // namespace binance

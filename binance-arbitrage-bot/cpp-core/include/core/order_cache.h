#pragma once

#include "binance/types.h"
#include <string>
#include <unordered_map>
#include <vector>
#include <mutex>

namespace binance {

/// Cache for tracking active orders
class OrderCache {
public:
    /// Add order to cache
    void add_order(const OrderResult& order);

    /// Get order by ID
    std::optional<OrderResult> get_order(uint64_t order_id) const;

    /// Get all orders
    std::vector<OrderResult> get_all_orders() const;

    /// Remove order from cache
    void remove_order(uint64_t order_id);

    /// Clear all orders
    void clear();

private:
    std::unordered_map<uint64_t, OrderResult> orders_;
    mutable std::mutex mutex_;
};

} // namespace binance

#include "core/price_monitor.h"
#include "utils/logger.h"
#include <algorithm>
#include <cmath>

namespace binance {

PriceMonitor::PriceMonitor() : running_(false) {
    LOG_INFO("PriceMonitor initialized");
}

PriceMonitor::~PriceMonitor() {
    stop();
}

void PriceMonitor::update_price(const std::string& symbol, double price) {
    // Lock-free atomic update
    prices_[symbol].store(price, std::memory_order_release);
}

double PriceMonitor::get_price(const std::string& symbol) const {
    auto it = prices_.find(symbol);
    if (it == prices_.end()) {
        return 0.0;
    }
    // Lock-free atomic read
    return it->second.load(std::memory_order_acquire);
}

bool PriceMonitor::has_symbol(const std::string& symbol) const {
    return prices_.find(symbol) != prices_.end();
}

void PriceMonitor::add_symbol(const std::string& symbol) {
    std::unique_lock<std::shared_mutex> lock(symbols_mutex_);

    if (std::find(symbols_.begin(), symbols_.end(), symbol) == symbols_.end()) {
        symbols_.push_back(symbol);
        prices_[symbol].store(0.0, std::memory_order_release);
    }
}

std::vector<std::string> PriceMonitor::get_symbols() const {
    std::shared_lock<std::shared_mutex> lock(symbols_mutex_);
    return symbols_;
}

size_t PriceMonitor::symbol_count() const {
    std::shared_lock<std::shared_mutex> lock(symbols_mutex_);
    return symbols_.size();
}

void PriceMonitor::clear() {
    std::unique_lock<std::shared_mutex> lock(symbols_mutex_);
    symbols_.clear();
    prices_.clear();
}

void PriceMonitor::start() {
    running_.store(true, std::memory_order_release);
    LOG_INFO("PriceMonitor started");
}

void PriceMonitor::stop() {
    running_.store(false, std::memory_order_release);
    LOG_INFO("PriceMonitor stopped");
}

bool PriceMonitor::is_running() const {
    return running_.load(std::memory_order_acquire);
}

std::vector<ArbitrageOpportunity> PriceMonitor::scan_triangular(double min_profit_percent) const {
    std::vector<ArbitrageOpportunity> opportunities;

    // TODO: Implement triangular arbitrage detection algorithm
    // This is a placeholder - full implementation in Phase 5

    LOG_DEBUG("Scanning for triangular arbitrage opportunities");

    return opportunities;
}

std::pair<std::string, std::string> PriceMonitor::parse_symbol(const std::string& symbol) const {
    // Simplified parser - assumes symbol format like "BTCUSDT"
    // TODO: Implement robust symbol parser

    if (symbol.size() >= 6) {
        std::string base = symbol.substr(0, 3);
        std::string quote = symbol.substr(3);
        return {base, quote};
    }

    return {"", ""};
}

} // namespace binance

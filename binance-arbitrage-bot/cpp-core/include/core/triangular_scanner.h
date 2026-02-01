#pragma once

#include "binance/types.h"
#include <vector>
#include <string>

namespace binance {

/// Scans for and detects triangular arbitrage opportunities
class TriangularScanner {
public:
    /// Scan for triangular opportunities given current prices
    static std::vector<ArbitrageOpportunity> scan(
        const std::unordered_map<std::string, double>& prices,
        double min_profit_percent
    );

private:
    /// DFS helper for cycle detection
    static void dfs(
        const std::string& start,
        const std::string& current,
        std::vector<std::string>& path,
        double profit_multiplier,
        const std::vector<std::string>& symbols,
        const std::unordered_map<std::string, double>& prices,
        std::vector<ArbitrageOpportunity>& opportunities,
        double min_profit_percent
    );
};

} // namespace binance

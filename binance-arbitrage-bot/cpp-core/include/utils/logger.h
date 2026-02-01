#pragma once

#include "binance/constants.h"
#include <string>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <mutex>

namespace binance {

/// Simple thread-safe logger
class Logger {
public:
    /// Get singleton instance
    static Logger& instance() {
        static Logger logger;
        return logger;
    }

    /// Set log level
    void set_level(LogLevel level) {
        level_ = level;
    }

    /// Log a message
    void log(LogLevel level, const std::string& message) {
        if (level < level_) {
            return;  // Skip messages below current level
        }

        std::lock_guard<std::mutex> lock(mutex_);

        // Timestamp
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);

        // Level prefix
        const char* level_str = "";
        switch (level) {
            case LogLevel::Debug: level_str = "[DEBUG]"; break;
            case LogLevel::Info: level_str = "[INFO ]"; break;
            case LogLevel::Warning: level_str = "[WARN ]"; break;
            case LogLevel::Error: level_str = "[ERROR]"; break;
            case LogLevel::Critical: level_str = "[CRIT ]"; break;
        }

        // Print
        std::cout << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
                  << " " << level_str << " " << message << std::endl;
    }

    /// Log debug message
    void debug(const std::string& message) { log(LogLevel::Debug, message); }

    /// Log info message
    void info(const std::string& message) { log(LogLevel::Info, message); }

    /// Log warning message
    void warning(const std::string& message) { log(LogLevel::Warning, message); }

    /// Log error message
    void error(const std::string& message) { log(LogLevel::Error, message); }

    /// Log critical message
    void critical(const std::string& message) { log(LogLevel::Critical, message); }

private:
    Logger() : level_(LogLevel::Info) {}

    LogLevel level_;
    std::mutex mutex_;
};

// Convenience macros
#define LOG_DEBUG(msg) binance::Logger::instance().debug(msg)
#define LOG_INFO(msg) binance::Logger::instance().info(msg)
#define LOG_WARNING(msg) binance::Logger::instance().warning(msg)
#define LOG_ERROR(msg) binance::Logger::instance().error(msg)
#define LOG_CRITICAL(msg) binance::Logger::instance().critical(msg)

} // namespace binance

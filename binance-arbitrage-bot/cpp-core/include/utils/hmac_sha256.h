#pragma once

#include <string>
#include <vector>
#include <cstdint>

namespace binance {

/// HMAC-SHA256 cryptographic signing
class HmacSHA256 {
public:
    /// Compute HMAC-SHA256 signature
    /// @param key Secret key
    /// @param data Data to sign
    /// @return Hex-encoded signature (64 characters)
    static std::string compute(const std::string& key, const std::string& data);

    /// Compute HMAC-SHA256 signature (binary output)
    /// @param key Secret key
    /// @param data Data to sign
    /// @return Binary signature (32 bytes)
    static std::vector<uint8_t> compute_binary(const std::string& key, const std::string& data);

private:
    /// Convert binary data to hex string
    static std::string to_hex(const std::vector<uint8_t>& data);
};

} // namespace binance

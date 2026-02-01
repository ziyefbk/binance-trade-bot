#include "utils/hmac_sha256.h"
#include <sstream>
#include <iomanip>

// Check if OpenSSL is available at compile time
#if __has_include(<openssl/hmac.h>)
#include <openssl/hmac.h>
#include <openssl/evp.h>
#define HAS_OPENSSL 1
#endif

namespace binance {

std::string HmacSHA256::compute(const std::string& key, const std::string& data) {
    auto binary = compute_binary(key, data);
    return to_hex(binary);
}

std::vector<uint8_t> HmacSHA256::compute_binary(const std::string& key, const std::string& data) {
#ifdef HAS_OPENSSL
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len = 0;

    HMAC(EVP_sha256(),
         key.c_str(),
         static_cast<int>(key.size()),
         reinterpret_cast<const unsigned char*>(data.c_str()),
         data.size(),
         digest,
         &digest_len);

    return std::vector<uint8_t>(digest, digest + digest_len);
#else
    // Placeholder implementation without OpenSSL
    // WARNING: This is NOT secure - only for compilation testing
    // Install OpenSSL for production use
    (void)key;   // Suppress unused parameter warning
    (void)data;
    return std::vector<uint8_t>(32, 0);  // Return dummy 32-byte hash
#endif
}

std::string HmacSHA256::to_hex(const std::vector<uint8_t>& data) {
    std::ostringstream oss;
    for (uint8_t byte : data) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    return oss.str();
}

} // namespace binance

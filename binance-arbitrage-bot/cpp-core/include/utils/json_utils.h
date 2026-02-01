#pragma once

#include <string>
#include <vector>
#include <optional>
#include <rapidjson/document.h>

namespace binance {

/// JSON utilities using RapidJSON
class JsonUtils {
public:
    using JsonValue = rapidjson::Value;
    using JsonDocument = rapidjson::Document;

    /// Parse JSON string
    static JsonDocument parse(const std::string& json_str);

    /// Parse JSON string in-situ (modifies input buffer)
    static JsonDocument parse_insitu(char* json_buffer);

    /// Extract double from JSON value with error handling
    static std::optional<double> get_double(const JsonValue& obj, const char* key);

    /// Extract int64 from JSON value with error handling
    static std::optional<int64_t> get_int64(const JsonValue& obj, const char* key);

    /// Extract string from JSON value with error handling
    static std::optional<std::string> get_string(const JsonValue& obj, const char* key);

    /// Extract bool from JSON value with error handling
    static std::optional<bool> get_bool(const JsonValue& obj, const char* key);

    /// Check if key exists in JSON object
    static bool has_member(const JsonValue& obj, const char* key);

    /// Convert JsonValue to pretty-printed string
    static std::string to_string(const JsonValue& value);

    /// Convert JsonValue to compact string
    static std::string to_string_compact(const JsonValue& value);

private:
    JsonUtils() = delete;  // Static utility class
};

} // namespace binance

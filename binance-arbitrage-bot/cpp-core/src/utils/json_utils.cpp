#include "utils/json_utils.h"
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/prettywriter.h>

namespace binance {

JsonUtils::JsonDocument JsonUtils::parse(const std::string& json_str) {
    JsonDocument doc;
    doc.Parse(json_str.c_str());
    return doc;
}

JsonUtils::JsonDocument JsonUtils::parse_insitu(char* json_buffer) {
    JsonDocument doc;
    doc.ParseInsitu(json_buffer);
    return doc;
}

std::optional<double> JsonUtils::get_double(const JsonValue& obj, const char* key) {
    if (!obj.IsObject() || !obj.HasMember(key)) {
        return std::nullopt;
    }
    const auto& value = obj[key];
    if (value.IsDouble()) {
        return value.GetDouble();
    } else if (value.IsInt()) {
        return static_cast<double>(value.GetInt());
    } else if (value.IsString()) {
        try {
            return std::stod(value.GetString());
        } catch (...) {
            return std::nullopt;
        }
    }
    return std::nullopt;
}

std::optional<int64_t> JsonUtils::get_int64(const JsonValue& obj, const char* key) {
    if (!obj.IsObject() || !obj.HasMember(key)) {
        return std::nullopt;
    }
    const auto& value = obj[key];
    if (value.IsInt64()) {
        return value.GetInt64();
    } else if (value.IsString()) {
        try {
            return std::stoll(value.GetString());
        } catch (...) {
            return std::nullopt;
        }
    }
    return std::nullopt;
}

std::optional<std::string> JsonUtils::get_string(const JsonValue& obj, const char* key) {
    if (!obj.IsObject() || !obj.HasMember(key)) {
        return std::nullopt;
    }
    const auto& value = obj[key];
    if (value.IsString()) {
        return std::string(value.GetString());
    }
    return std::nullopt;
}

std::optional<bool> JsonUtils::get_bool(const JsonValue& obj, const char* key) {
    if (!obj.IsObject() || !obj.HasMember(key)) {
        return std::nullopt;
    }
    const auto& value = obj[key];
    if (value.IsBool()) {
        return value.GetBool();
    }
    return std::nullopt;
}

bool JsonUtils::has_member(const JsonValue& obj, const char* key) {
    return obj.IsObject() && obj.HasMember(key);
}

std::string JsonUtils::to_string(const JsonValue& value) {
    rapidjson::StringBuffer buffer;
    rapidjson::PrettyWriter<rapidjson::StringBuffer> writer(buffer);
    value.Accept(writer);
    return buffer.GetString();
}

std::string JsonUtils::to_string_compact(const JsonValue& value) {
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    value.Accept(writer);
    return buffer.GetString();
}

} // namespace binance

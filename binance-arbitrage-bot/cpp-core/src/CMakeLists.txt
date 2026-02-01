# ============================================================================
# MAIN C++ LIBRARY: binance_engine
# ============================================================================

# Source files
set(BINANCE_ENGINE_SOURCES
    # Binance API clients
    binance/types.cpp
    binance/rest_client.cpp
    binance/websocket_client.cpp
    binance/engine.cpp

    # Core engine components
    core/price_monitor.cpp
    core/order_executor.cpp
    core/rate_limiter.cpp
    core/order_cache.cpp
    core/triangular_scanner.cpp

    # Utilities
    utils/logger.cpp
    utils/timer.cpp
    utils/hmac_sha256.cpp
    utils/json_utils.cpp
)

# Create static library
add_library(binance_engine STATIC ${BINANCE_ENGINE_SOURCES})

# ============================================================================
# INCLUDE DIRECTORIES
# ============================================================================

target_include_directories(binance_engine
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

# ============================================================================
# LINK DEPENDENCIES
# ============================================================================

# Link found dependencies (conditionally)
if(Boost_FOUND)
    target_link_libraries(binance_engine PUBLIC Boost::system)
else()
    message(STATUS "WARNING: Boost::system will not be linked")
endif()

if(OpenSSL_FOUND)
    target_link_libraries(binance_engine PUBLIC OpenSSL::Crypto OpenSSL::SSL)
else()
    message(STATUS "WARNING: OpenSSL will not be linked")
endif()

if(RapidJSON_FOUND)
    target_link_libraries(binance_engine PRIVATE RapidJSON::rapidjson)
else()
    message(STATUS "WARNING: RapidJSON will not be linked")
endif()

# ============================================================================
# COMPILE FEATURES
# ============================================================================

target_compile_features(binance_engine PUBLIC cxx_std_17)

# ============================================================================
# COMPILER WARNINGS & FLAGS
# ============================================================================

if(MSVC)
    target_compile_options(binance_engine PRIVATE /W4 /WX)
else()
    target_compile_options(binance_engine PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

# ============================================================================
# LOGGING
# ============================================================================

message(STATUS "Creating library: binance_engine")
message(STATUS "  Sources: ${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "  Headers: ${CMAKE_CURRENT_SOURCE_DIR}/../include")

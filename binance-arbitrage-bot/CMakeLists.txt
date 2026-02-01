cmake_minimum_required(VERSION 3.15)
project(binance-arbitrage-bot
    VERSION 1.0.0
    DESCRIPTION "Low-latency cryptocurrency arbitrage trading bot"
    LANGUAGES CXX
)

# ============================================================================
# C++ STANDARD
# ============================================================================
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================================
# COMPILER FLAGS
# ============================================================================
if(MSVC)
    # Visual Studio
    add_compile_options(/W4 /WX /permissive-)
else()
    # GCC / Clang
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)

    # Release optimization flags
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        add_compile_options(-O3 -march=native -flto)
    endif()

    # Debug flags with sanitizers
    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        add_compile_options(-g -O0)
        option(ENABLE_ASAN "Enable AddressSanitizer" ON)
        option(ENABLE_TSAN "Enable ThreadSanitizer" OFF)

        if(ENABLE_ASAN)
            add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
            add_link_options(-fsanitize=address)
        endif()

        if(ENABLE_TSAN)
            add_compile_options(-fsanitize=thread)
            add_link_options(-fsanitize=thread)
        endif()
    endif()
endif()

# ============================================================================
# FIND DEPENDENCIES
# ============================================================================

# Boost
find_package(Boost 1.70 QUIET COMPONENTS system)
if(Boost_FOUND)
    message(STATUS "✓ Boost found: ${Boost_VERSION}")
else()
    message(STATUS "⚠ Boost NOT found (install with: vcpkg install boost:x64-windows)")
endif()

# OpenSSL
find_package(OpenSSL QUIET)
if(OpenSSL_FOUND)
    message(STATUS "✓ OpenSSL found: ${OPENSSL_VERSION}")
else()
    message(STATUS "⚠ OpenSSL NOT found (install with: vcpkg install openssl:x64-windows)")
endif()

# RapidJSON
find_package(RapidJSON QUIET)
if(RapidJSON_FOUND)
    message(STATUS "✓ RapidJSON found")
else()
    message(STATUS "⚠ RapidJSON NOT found (install with: vcpkg install rapidjson:x64-windows)")
endif()

# Pybind11 (optional, for Python bindings)
find_package(pybind11 QUIET)

# Google Test (optional, for testing)
find_package(GTest QUIET)

# Google Benchmark (optional, for benchmarking)
find_package(benchmark QUIET)

# ============================================================================
# OUTPUT DIRECTORIES
# ============================================================================
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# ============================================================================
# ADD SUBDIRECTORIES
# ============================================================================

# Main C++ library
add_subdirectory(cpp-core/src)

# Python bindings (if pybind11 is found)
if(pybind11_FOUND)
    add_subdirectory(python-bindings)
endif()

# Tests (if GTest is found)
if(GTest_FOUND)
    enable_testing()
    add_subdirectory(cpp-core/tests)
endif()

# Benchmarks (if Google Benchmark is found)
if(benchmark_FOUND)
    add_subdirectory(cpp-core/benchmarks)
endif()

# ============================================================================
# SUMMARY
# ============================================================================
message(STATUS "")
message(STATUS "================== BUILD SUMMARY ==================")
message(STATUS "C++ Standard: C++${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Boost: ${Boost_FOUND}")
message(STATUS "OpenSSL: ${OpenSSL_FOUND}")
message(STATUS "RapidJSON: ${RapidJSON_FOUND}")
message(STATUS "Pybind11: ${pybind11_FOUND}")
message(STATUS "Google Test: ${GTest_FOUND}")
message(STATUS "Google Benchmark: ${benchmark_FOUND}")
message(STATUS "====================================================")
message(STATUS "")
message(STATUS "NOTE: To install missing dependencies, use vcpkg:")
message(STATUS "  vcpkg install boost:x64-windows openssl:x64-windows rapidjson:x64-windows")
message(STATUS "")

# WSL 开发环境设置指南

## 概述

本项目已在 Phase 1 完成了 C++ 核心架构的设计和基础文件创建。现在迁移到 WSL (Windows Subsystem for Linux) 进行开发。

## WSL 中的优势

- ✅ 原生 Linux 工具链（GCC/Clang）
- ✅ 包管理更成熟（apt）
- ✅ 开发体验更好
- ✅ 性能更接近生产环境

## WSL 初始化步骤

### 1. 安装依赖项

```bash
# 更新包管理器
sudo apt-get update

# 安装构建工具
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget

# 安装 C++ 依赖
sudo apt-get install -y \
    libboost-all-dev \
    libssl-dev \
    rapidjson-dev \
    python3-dev

# 安装性能工具
sudo apt-get install -y \
    google-benchmark-dev \
    googletest \
    valgrind \
    linux-tools-generic

# 安装 Pybind11（Python 绑定）
sudo apt-get install -y pybind11-dev
# 或通过 pip
pip install pybind11
```

### 2. 配置项目

```bash
cd /mnt/c/Users/28275/Desktop/bian/binance-arbitrage-bot
mkdir -p build
cd build

# 配置 CMake
cmake .. -DCMAKE_BUILD_TYPE=Release

# 或带 sanitizers（Debug）
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON
```

### 3. 构建项目

```bash
# 构建库
cmake --build . --parallel 8

# 运行测试（当完成时）
ctest --output-on-failure

# 运行基准测试（当完成时）
./benchmarks/price_monitor_benchmark
```

## 项目结构总结

### Phase 1 已完成（✅）

**头文件** (13 个):
- `binance/types.h` - 所有核心数据结构
- `binance/constants.h` - API 常量和费率
- `binance/engine.h` - 主交易引擎
- `binance/rest_client.h` - REST API 客户端
- `binance/websocket_client.h` - WebSocket 客户端
- `core/price_monitor.h` - 无锁价格缓存 ⭐ 性能关键
- `core/rate_limiter.h` - 令牌桶速率限制
- `core/order_cache.h` - 订单追踪缓存
- `core/order_executor.h` - 订单执行器
- `core/triangular_scanner.h` - 三角套利检测
- `utils/logger.h` - 线程安全日志
- `utils/timer.h` - 纳秒级计时
- `utils/hmac_sha256.h` - HMAC-SHA256 签名

**实现文件** (14 个):
- 所有对应的 `.cpp` 实现文件（部分为 Phase 2-6 的占位符）

**构建配置** (2 个):
- 根 `CMakeLists.txt` - 依赖管理
- `cpp-core/src/CMakeLists.txt` - 库编译

### Phase 2-7 任务列表

| 阶段 | 任务 | 状态 |
|------|------|------|
| Phase 2 | 实现无锁数据结构 (PriceMonitor, RateLimiter) | 📋 待开始 |
| Phase 3 | 实现 REST API 客户端 | 📋 待开始 |
| Phase 4 | 实现 WebSocket 客户端 | 📋 待开始 |
| Phase 5 | 实现订单执行器和三角套利 | 📋 待开始 |
| Phase 6 | 集成主引擎和 Python 绑定 | 📋 待开始 |
| Phase 7 | CMake、测试、基准测试 | 📋 待开始 |

## VSCode + WSL 开发建议

### 安装 VSCode 扩展

```bash
# Remote - WSL
# C/C++ IntelliSense
# CMake Tools
```

### WSL 中使用 VSCode

```bash
# 在 WSL 中打开项目
cd /mnt/c/Users/28275/Desktop/bian/binance-arbitrage-bot
code .
```

### 推荐的 .vscode/settings.json

```json
{
    "C_Cpp.intelliSenseEngine": "Tag Parser",
    "C_Cpp.codeAnalysis.enabled": true,
    "C_Cpp.codeAnalysis.runAutomatically": true,
    "cmake.configureOnOpen": true,
    "cmake.buildDirectory": "${workspaceFolder}/build"
}
```

## 常用命令

```bash
# 构建
cd build && cmake --build . --parallel 8

# 清理
rm -rf build && mkdir build

# 运行单个测试（完成后）
./build/bin/engine_test --gtest_filter=PriceMonitor*

# 性能分析
valgrind --tool=callgrind ./build/benchmarks/price_monitor_benchmark

# 代码格式检查
clang-format -i cpp-core/**/*.cpp cpp-core/**/*.h
```

## 遇到问题？

### 缺少依赖
```bash
# 检查已安装的库
apt list --installed | grep -E "boost|openssl|rapidjson"

# 安装缺失的库
sudo apt-get install libboost-system-dev
```

### CMake 错误
```bash
# 清理构建目录
rm -rf build

# 重新配置
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc-11 -DCMAKE_CXX_COMPILER=g++-11
```

### 编译错误
```bash
# 使用详细输出
make VERBOSE=1

# 检查所有编译警告
cmake --build . -- VERBOSE=1
```

## 性能优化提示

### 编译标志
```bash
# Release 编译（优化）
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-O3 -march=native -flto"

# Debug 编译（调试）
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON -DENABLE_TSAN=OFF
```

### 性能测试
```bash
# Google Benchmark（完成后）
./build/benchmarks/price_monitor_benchmark --benchmark_repetitions=10

# perf 分析
sudo perf record -g ./build/benchmarks/price_monitor_benchmark
sudo perf report
```

## 下一步

1. ✅ **现在**: WSL 中验证编译（Phase 1 验证）
2. 📋 **Phase 2**: 实现 PriceMonitor 和 RateLimiter
3. 📋 **Phase 3**: REST API 和 HMAC 签名实现
4. 📋 **Phase 4**: WebSocket 客户端实现
5. 📋 **Phase 5**: 订单执行和三角套利
6. 📋 **Phase 6**: Python 绑定集成
7. 📋 **Phase 7**: 完整测试和性能优化

## 参考资源

- [CMake 官方教程](https://cmake.org/cmake/help/latest/guide/tutorial/)
- [Boost 库文档](https://www.boost.org/doc/)
- [RapidJSON 文档](https://rapidjson.org/)
- [Pybind11 文档](https://pybind11.readthedocs.io/)
- [Google Test 文档](https://google.github.io/googletest/)
- [Google Benchmark](https://github.com/google/benchmark)

---

**最后更新**: 2026-02-01
**当前状态**: Phase 1 完成，准备迁移到 WSL

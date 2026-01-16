# 本地快速启动指南 (Conda 环境)

由于 Docker 构建遇到网络问题，这里提供本地 conda 环境的快速启动方式。

## 环境信息

- **Python**: 3.11.0
- **Conda 环境**: math
- **路径**: `D:/Anaconda3/envs/math`

## ✅ 已验证的依赖

所有必需的 Python 包已安装：
- PyYAML 6.0.3
- Pandas 2.3.2
- NumPy 2.2.6
- Rich 14.2.0
- Matplotlib 3.10.3
- Plotly 6.5.2

## 🚀 快速测试

### 1. 运行环境测试

```bash
cd c:\Users\28275\Desktop\bian\binance-arbitrage-bot\python-strategy
D:/Anaconda3/envs/math/python.exe test_environment.py
```

**预期输出**: 所有测试项显示 `[OK]`

### 2. 下一步：编译 Rust 模块

#### 方式 1: 使用 pip 安装 maturin

```bash
# 安装 maturin
D:/Anaconda3/envs/math/python.exe -m pip install -i https://pypi.org/simple maturin

# 进入 rust-core 目录
cd c:\Users\28275\Desktop\bian\binance-arbitrage-bot\rust-core

# 编译 Rust 模块（开发模式）
D:/Anaconda3/envs/math/Scripts/maturin.exe develop

# 或编译发布版本（更快）
D:/Anaconda3/envs/math/Scripts/maturin.exe develop --release
```

#### 方式 2: 验证 Rust 工具链

```bash
# 检查 Rust 是否已安装
rustc --version
cargo --version

# 如果没有安装 Rust，访问: https://rustup.rs/
```

### 3. 验证 Rust 模块安装

```bash
cd c:\Users\28275\Desktop\bian\binance-arbitrage-bot\python-strategy
D:/Anaconda3/envs/math/python.exe -c "import binance_rust_py; print('Rust module loaded successfully!')"
```

## 📝 运行模式

### 回测模式（无需 API）

```bash
cd c:\Users\28275\Desktop\bian\binance-arbitrage-bot\python-strategy
D:/Anaconda3/envs/math/python.exe main.py --backtest
```

### 测试网模式（需要测试网 API）

```bash
# 1. 配置测试网 API
# 编辑 c:\Users\28275\Desktop\bian\binance-arbitrage-bot\config\config.yaml

# 2. 运行测试网模式
D:/Anaconda3/envs/math/python.exe main.py --testnet
```

### 实盘模式（⚠️ 谨慎使用）

```bash
D:/Anaconda3/envs/math/python.exe main.py --live
```

## 🔧 故障排查

### 问题 1: Rust 模块编译失败

**可能原因**:
- Rust 工具链未安装
- 缺少 C++ 编译器 (Windows 需要 Visual Studio Build Tools)

**解决方法**:
1. 安装 Rust: https://rustup.rs/
2. 安装 Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
   - 选择 "Desktop development with C++"

### 问题 2: Python 模块导入失败

**解决方法**:
```bash
# 确保在正确的目录
cd c:\Users\28275\Desktop\bian\binance-arbitrage-bot\python-strategy

# 重新运行测试
D:/Anaconda3/envs/math/python.exe test_environment.py
```

### 问题 3: 配置文件错误

**解决方法**:
```bash
# 检查配置文件是否存在
dir ..\config\config.yaml

# 如果不存在，从模板复制
copy ..\config\config.example.yaml ..\config\config.yaml
```

## 📚 重要文件路径

- 项目根目录: `c:\Users\28275\Desktop\bian\binance-arbitrage-bot`
- Python 策略: `binance-arbitrage-bot\python-strategy`
- Rust 核心: `binance-arbitrage-bot\rust-core`
- 配置文件: `binance-arbitrage-bot\config\config.yaml`

## 💡 推荐工作流

### 阶段 1: 环境验证（当前）
1. ✅ Python 依赖测试通过
2. ⏳ 编译 Rust 模块
3. ⏳ 验证 Rust-Python 集成

### 阶段 2: 功能测试
1. 运行回测模式
2. 检查策略逻辑
3. 调整参数

### 阶段 3: 实盘准备
1. 测试网验证
2. 小额实盘测试
3. 监控和优化

## ⚠️ 注意事项

1. **回测模式最安全** - 不需要 API，可以随意测试
2. **测试网用虚拟资金** - 用于验证连接和订单执行
3. **实盘需谨慎** - 从小额开始，设置严格止损

## 🆘 需要帮助？

如果遇到问题：
1. 查看项目文档: [README.md](../README.md)
2. 查看编译指南: [COMPILE_GUIDE.md](../COMPILE_GUIDE.md)
3. 查看测试总结: [TEST_SUMMARY.md](../TEST_SUMMARY.md)

---

**最后更新**: 2026-01-16
**环境状态**: Python ✅ | Rust ⏳

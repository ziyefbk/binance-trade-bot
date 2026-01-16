# 编译和运行指南

## 📋 当前状态

✅ **已完成**:
- 项目结构完整
- 所有代码文件已创建
- 文档完善
- 配置文件准备就绪
- GitHub 远程仓库已推送

⚠️ **待完成**:
- Rust 核心编译
- Python 依赖安装
- 运行测试

---

## 🔧 环境要求

### 1. Rust 环境
- **Rust 版本**: 1.75+
- **工具链**: stable

```bash
# 检查 Rust 版本
rustc --version
cargo --version
```

### 2. Python 环境
- **Python 版本**: 3.7+（推荐 3.11）
- **已确认可用环境**: `D:/anaconda3/envs/math` (Python 3.11.0)

```bash
# 检查 Python 版本
D:/anaconda3/envs/math/python.exe --version
```

### 3. 必需工具
- **maturin**: 用于编译 Rust-Python 绑定

---

## 📦 完整安装流程

### 步骤 1: 安装 Maturin

```bash
# 方式 1: 使用 pip 安装到 math 环境
D:/anaconda3/envs/math/python.exe -m pip install maturin

# 方式 2: 使用 cargo 安装（推荐）
cargo install maturin
```

### 步骤 2: 编译 Rust 核心

```bash
cd rust-core

# 开发模式编译（快速，用于调试）
maturin develop

# 或者发布模式（优化，用于生产）
maturin build --release
```

**注意事项**:
- 首次编译需要 5-10 分钟（下载和编译依赖）
- PyO3 使用 `abi3-py37` 特性，支持 Python 3.7+
- 确保使用 math 环境的 Python:
  ```bash
  export PATH="/d/anaconda3/envs/math:$PATH"
  maturin develop
  ```

### 步骤 3: 安装 Python 依赖

```bash
cd ../python-strategy

# 使用 math 环境安装依赖
D:/anaconda3/envs/math/python.exe -m pip install -r requirements.txt

# 如果遇到网络问题，使用国内镜像
D:/anaconda3/envs/math/python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**依赖列表**:
- pyyaml >= 6.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- plotly >= 5.14.0
- rich >= 13.0.0
- pytest >= 7.4.0
- pytest-cov >= 4.1.0

### 步骤 4: 验证安装

```bash
# 测试 Rust 模块是否可导入
D:/anaconda3/envs/math/python.exe -c "from binance_rust_py import BinanceEngine; print('✓ Rust 模块导入成功')"
```

---

## 🧪 运行测试

### 1. Rust 单元测试

```bash
cd rust-core

# 运行所有测试
cargo test

# 运行特定测试
cargo test binance

# 查看测试覆盖率（需要 tarpaulin）
cargo tarpaulin --out Html
```

### 2. Python 回测模式（无需 Rust 编译）

```bash
cd python-strategy

# 运行回测
D:/anaconda3/envs/math/python.exe main.py --backtest
```

**回测说明**:
- 使用模拟数据（2024-01-01 到 2024-01-31）
- 初始资金: 1000 USDT
- 生成 HTML 可视化图表在 `backtest_plots/` 目录

### 3. 测试网模式（需要 Rust 编译）

⚠️ **前置条件**:
1. 完成 Rust 编译（步骤 2）
2. 配置币安 API 密钥

```bash
# 1. 编辑配置文件
cp config/config.example.yaml config/config.yaml
# 编辑 config.yaml，填入测试网 API 密钥

# 2. 运行测试网模式
D:/anaconda3/envs/math/python.exe main.py --testnet
```

**获取测试网 API 密钥**:
1. 访问: https://testnet.binance.vision/
2. 创建 API Key
3. 仅勾选"读取"和"现货交易"权限

---

## 🐛 常见问题

### 问题 1: `maturin: command not found`

**原因**: maturin 未安装或不在 PATH 中

**解决方案**:
```bash
# 使用 cargo 安装
cargo install maturin

# 或使用 pip 安装
D:/anaconda3/envs/math/python.exe -m pip install maturin

# 验证安装
maturin --version
```

### 问题 2: Python 版本过低

**错误信息**: `the configured Python interpreter version (3.6) is lower than PyO3's minimum supported version (3.7)`

**解决方案**: 使用 Python 3.7+ 环境
```bash
# 使用 math 环境（Python 3.11）
export PATH="/d/anaconda3/envs/math:$PATH"
maturin develop
```

### 问题 3: 网络代理问题

**错误信息**: `ProxyError('Cannot connect to proxy.'...)`

**解决方案**:
```bash
# 使用 --no-proxy 参数
D:/anaconda3/envs/math/python.exe -m pip install package-name --no-proxy

# 或使用国内镜像
D:/anaconda3/envs/math/python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 4: Rust 编译错误

**常见原因**:
- 依赖版本冲突
- 网络问题（无法下载 crate）

**解决方案**:
```bash
# 清理缓存重新编译
cd rust-core
cargo clean
cargo build

# 如果网络问题，配置国内镜像
# 编辑 ~/.cargo/config.toml
[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "git://mirrors.ustc.edu.cn/crates.io-index"
```

### 问题 5: 无法导入 binance_rust_py

**原因**: Rust 模块未编译或 Python 环境不匹配

**解决方案**:
```bash
# 1. 确认在正确的目录
cd rust-core

# 2. 重新编译
maturin develop

# 3. 测试导入
D:/anaconda3/envs/math/python.exe -c "import binance_rust_py; print(dir(binance_rust_py))"
```

---

## 📝 快速开始命令汇总

```bash
# 克隆项目（如果从 GitHub）
git clone https://github.com/ziyefbk/binance-trade-bot.git
cd binance-trade-bot

# 1. 安装 Maturin
cargo install maturin

# 2. 编译 Rust 核心
cd rust-core
export PATH="/d/anaconda3/envs/math:$PATH"
maturin develop
cd ..

# 3. 安装 Python 依赖
cd python-strategy
D:/anaconda3/envs/math/python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 配置 API 密钥
cp config/config.example.yaml config/config.yaml
# 编辑 config.yaml

# 5. 运行回测（无需 API）
D:/anaconda3/envs/math/python.exe main.py --backtest

# 6. 运行测试网
D:/anaconda3/envs/math/python.exe main.py --testnet
```

---

## 📊 性能基准

### 编译时间
- **首次编译**: 5-10 分钟（下载依赖）
- **增量编译**: 30-60 秒
- **发布模式**: 10-15 分钟（LTO 优化）

### 运行性能
- **WebSocket 延迟**: < 50ms（目标）
- **订单执行**: < 100ms（目标）
- **三角套利全流程**: < 200ms（目标）
- **Python 调用 Rust**: < 1ms（目标）

---

## 🔗 相关文档

- **快速开始**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **接口规范**: [docs/interfaces.md](docs/interfaces.md)
- **任务分配**: [docs/agent_tasks.md](docs/agent_tasks.md)
- **项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **README**: [README.md](README.md)

---

## 💡 开发提示

### 代码检查
```bash
# Rust 代码检查
cd rust-core
cargo clippy
cargo fmt --check

# Python 代码检查
cd python-strategy
D:/anaconda3/envs/math/python.exe -m pylint .
D:/anaconda3/envs/math/python.exe -m black --check .
```

### 性能分析
```bash
# Rust 性能分析
cargo build --release
cargo flamegraph

# Python 性能分析
D:/anaconda3/envs/math/python.exe -m cProfile main.py --backtest
```

---

**🎉 准备好开始了吗？按照上述步骤逐步执行即可！**

**⚠️ 重要提示**:
- 先在测试网测试，确认稳定后再考虑实盘
- 小额测试（10-20 USDT）
- 严格风险控制
- 交易有风险，投资需谨慎

---

**最后更新**: 2025-01-16
**版本**: 1.0.0

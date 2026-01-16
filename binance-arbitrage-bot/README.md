# 币安套利机器人 (Binance Arbitrage Bot)

> **高性能 Rust + Python 混合架构** - 三角套利与资金费率套利混合策略

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/rust-1.75+-orange.svg)](https://www.rust-lang.org/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

---

## 项目概述

这是一个多 Agent 协作开发的币安套利机器人项目，采用 **Rust 核心 + Python 策略** 的混合架构，旨在实现：

- **三角套利**: 利用三个交易对之间的价格差异进行无风险套利
- **资金费率套利**: 通过现货-合约对冲赚取资金费率收益
- **混合策略**: 动态分配资金，最大化收益

### 核心特性

✅ **极致性能**: Rust 实现的高频交易引擎，订单执行延迟 < 100ms
✅ **实时监控**: WebSocket 实时价格流，毫秒级机会捕捉
✅ **智能风险控制**: 自动止损、仓位管理、爆仓保护
✅ **易于扩展**: Python 策略层，快速迭代新策略
✅ **全面回测**: 历史数据回测，验证策略有效性

---

## 项目结构

```
binance-arbitrage-bot/
├── rust-core/                 # Rust 核心引擎
│   ├── src/
│   │   ├── binance/          # 币安 API 客户端
│   │   ├── engine/           # 交易引擎
│   │   ├── utils/            # 工具函数
│   │   └── lib.rs            # PyO3 绑定
│   ├── Cargo.toml
│   └── pyproject.toml
│
├── python-strategy/           # Python 策略层
│   ├── strategies/           # 套利策略
│   ├── risk_management/      # 风险管理
│   ├── backtest/             # 回测系统
│   ├── monitor/              # 监控面板
│   └── main.py               # 主程序入口
│
├── config/                   # 配置文件
│   ├── config.example.yaml
│   └── trading_pairs.yaml
│
├── tests/                    # 测试
│   ├── rust_tests/
│   └── python_tests/
│
└── docs/                     # 文档
    ├── interfaces.md         # 接口规范（重要！）
    ├── architecture.md       # 架构设计
    └── agent_tasks.md        # Agent 任务分配
```

---

## 多 Agent 开发任务分配

本项目采用多 Agent 并行开发模式，各 Agent 负责独立模块开发。

### 总指挥 Agent（当前）

**职责**：
- ✅ 创建项目骨架和目录结构
- ✅ 定义接口规范文档
- ⏳ 协调各 Agent 集成
- ⏳ 代码审查和测试
- ⏳ 部署和上线

**关键文档**: [`docs/interfaces.md`](docs/interfaces.md) - **所有 Agent 必读！**

---

### Agent 1: Rust 币安 API 客户端

**任务**: 实现 Rust 币安 REST API 和 WebSocket 客户端

**交付文件**:
- `rust-core/src/binance/rest_client.rs`
- `rust-core/src/binance/websocket.rs`
- `rust-core/src/binance/types.rs`
- `rust-core/src/binance/mod.rs`

**验收标准**:
- [ ] REST API 所有端点通过单元测试
- [ ] WebSocket 能持续运行 1 小时不断线
- [ ] 速率限制自动处理（429 错误重试）
- [ ] 代码覆盖率 > 80%

**参考文档**: [docs/interfaces.md#1.1](docs/interfaces.md)

---

### Agent 2: Rust 交易引擎

**任务**: 实现订单执行引擎和价格监控系统

**交付文件**:
- `rust-core/src/engine/order_executor.rs`
- `rust-core/src/engine/price_monitor.rs`
- `rust-core/src/engine/rate_limiter.rs`
- `rust-core/src/engine/mod.rs`

**验收标准**:
- [ ] 订单执行延迟 < 100ms
- [ ] 价格监控器能同时处理 20+ 交易对
- [ ] 三角套利机会检测准确率 > 95%
- [ ] 压力测试：1000 次连续下单无失败

**参考文档**: [docs/interfaces.md#1.3-1.5](docs/interfaces.md)

---

### Agent 3: PyO3 绑定层

**任务**: 将 Rust 核心引擎暴露给 Python

**交付文件**:
- `rust-core/src/lib.rs`
- `rust-core/Cargo.toml`
- `rust-core/pyproject.toml`
- `binance_rust_py.pyi` (类型提示文件)

**验收标准**:
- [ ] `maturin develop` 成功编译
- [ ] Python 能正常导入和调用所有方法
- [ ] 类型提示完整，IDE 自动补全正常
- [ ] 性能测试：Python 调用 Rust 开销 < 1ms

**参考文档**: [docs/interfaces.md#1.6](docs/interfaces.md)

---

### Agent 4: Python 三角套利策略

**任务**: 实现三角套利策略和风险管理

**交付文件**:
- `python-strategy/strategies/triangular_arbitrage.py`
- `python-strategy/risk_management/position_manager.py`
- `python-strategy/risk_management/stop_loss.py`
- `python-strategy/config.py`
- `config/config.yaml`

**验收标准**:
- [ ] 能正确生成所有可能的三角路径
- [ ] 风险控制参数生效
- [ ] 模拟运行 24 小时无错误
- [ ] 回测收益率符合预期

**参考文档**: [docs/interfaces.md#2.2-2.3](docs/interfaces.md)

---

### Agent 5: Python 资金费率套利策略

**任务**: 实现合约资金费率套利策略

**交付文件**:
- `python-strategy/strategies/funding_rate.py`
- `python-strategy/strategies/hybrid.py`
- `python-strategy/utils/leverage_calculator.py`
- `python-strategy/utils/liquidation_monitor.py`

**验收标准**:
- [ ] 能正确获取资金费率
- [ ] 对冲仓位数量精确匹配
- [ ] 爆仓监控实时预警
- [ ] 回测年化收益 > 20%

**参考文档**: [docs/interfaces.md#2.4-2.5](docs/interfaces.md)

---

### Agent 6: Python 监控和可视化

**任务**: 实现实时监控面板和回测系统

**交付文件**:
- `python-strategy/monitor/dashboard.py`
- `python-strategy/monitor/logger.py`
- `python-strategy/backtest/engine.py`
- `python-strategy/backtest/visualization.py`
- `python-strategy/main.py`

**验收标准**:
- [ ] 监控面板每秒刷新数据
- [ ] 日志文件正常轮转
- [ ] 回测结果与实盘对比误差 < 5%
- [ ] 可视化图表清晰易读

**参考文档**: [docs/interfaces.md#2.6-2.8](docs/interfaces.md)

---

## 开发环境设置

### 前置要求

- **Rust**: 1.75+ ([安装指南](https://www.rust-lang.org/tools/install))
- **Python**: 3.10+ ([下载地址](https://www.python.org/downloads/))
- **Git**: 最新版本

### Rust 环境

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 验证安装
rustc --version
cargo --version

# 安装 Maturin（用于 Python 绑定）
pip install maturin
```

### Python 环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装 Python 依赖（待 Agent 4/5/6 创建 requirements.txt）
pip install -r python-strategy/requirements.txt
```

### Rust 项目初始化（Agent 1/2/3）

```bash
cd rust-core

# 初始化 Maturin 项目
maturin init

# 开发模式编译（快速测试）
maturin develop

# 发布模式编译（性能优化）
maturin build --release
```

---

## 开发工作流

### 1. 克隆仓库并创建分支

```bash
git clone <repository-url>
cd binance-arbitrage-bot

# 创建功能分支（根据你的 Agent 编号）
git checkout -b feature/agent-1-rest-api
# 或
git checkout -b feature/agent-2-engine
# 或
git checkout -b feature/agent-3-pyo3
# 等等...
```

### 2. 阅读接口规范

**必读**: [`docs/interfaces.md`](docs/interfaces.md)

这份文档定义了所有模块间的接口规范，确保你的代码能与其他 Agent 的代码无缝集成。

### 3. 开发和测试

```bash
# Rust 开发（Agent 1/2/3）
cd rust-core
cargo build
cargo test
cargo clippy  # 代码检查

# Python 开发（Agent 4/5/6）
cd python-strategy
pytest tests/
python -m pylint your_module.py
```

### 4. 提交代码

```bash
git add .
git commit -m "[Agent X] feat(module): 实现某某功能"
git push origin feature/agent-x-module
```

### 5. 创建 Pull Request

- 提交 PR 到 `develop` 分支
- 等待总指挥 Agent 审查
- 通过后合并到主分支

---

## 接口依赖关系

```
Agent 4/5/6 (Python 策略)
     ↓
Agent 3 (PyO3 绑定) ← **关键路径**
     ↓
Agent 1 (REST API) + Agent 2 (Engine)
```

**关键**: Agent 3 完成 PyO3 绑定后，Agent 4/5/6 才能开始 Python 开发。
**建议**: Agent 1 和 Agent 2 可以并行开发，共享 Rust 代码仓库。

---

## 测试策略

### 单元测试

每个模块必须有单元测试，覆盖率 > 80%。

**Rust**:
```bash
cd rust-core
cargo test
```

**Python**:
```bash
cd python-strategy
pytest tests/ --cov=. --cov-report=html
```

### 集成测试

由总指挥 Agent 负责，在所有模块完成后进行。

1. 测试网端到端测试
2. 性能压测
3. 稳定性测试（24 小时运行）

---

## 部署指南

### 🐳 Docker 部署（推荐）

**最简单的方式！** 无需手动配置 Rust/Python 环境，一键启动：

```bash
# 1. 启动 Docker Desktop（Windows）
# 在开始菜单中找到并启动 Docker Desktop

# 2. 快速启动
cd binance-arbitrage-bot

# Windows 用户（双击运行）:
start.bat

# Linux/Mac 用户:
./start.sh

# 或直接使用 Docker Compose:
docker-compose build  # 首次构建镜像
docker-compose up     # 启动回测模式
```

**详细指南**:
- 📖 [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署教程
- 📖 [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 详细指南

**运行模式**:
- ✅ 回测模式（默认）- 无需 API，安全验证
- ⚠️ 测试网模式 - 需要测试网 API
- ⚠️⚠️ 实盘模式 - 需要实盘 API，谨慎使用

### 本地开发环境（手动编译）

如果你需要修改代码或进行开发：

```bash
# 1. 编译 Rust 核心
cd rust-core
maturin develop

# 2. 配置 API 密钥
cp config/config.example.yaml config/config.yaml
# 编辑 config.yaml，填入你的币安 API 密钥

# 3. 运行（测试网）
cd python-strategy
python main.py --testnet
```

### 生产环境（VPS）

**推荐配置**:
- VPS 位置: 新加坡/香港（靠近币安服务器）
- 配置: 2核 4G 内存
- 系统: Ubuntu 22.04 LTS

#### 方式 1: Docker 部署（推荐）

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. 克隆项目
git clone <repository-url>
cd binance-arbitrage-bot

# 3. 配置 API
cp config/config.example.yaml config/config.yaml
nano config/config.yaml

# 4. 启动容器（后台运行）
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

#### 方式 2: 传统部署

```bash
# 1. 安装依赖
sudo apt update
sudo apt install -y build-essential python3-dev

# 2. 构建发布版本
cd rust-core
maturin build --release

# 3. 安装 wheel
pip install target/wheels/*.whl

# 4. 配置 systemd 守护进程
sudo cp deploy/arbitrage-bot.service /etc/systemd/system/
sudo systemctl enable arbitrage-bot
sudo systemctl start arbitrage-bot

# 5. 查看日志
journalctl -u arbitrage-bot -f
```

---

## 性能指标

### 目标性能

- WebSocket 接收延迟: < 50ms
- 订单执行延迟: < 100ms
- 三角套利全流程: < 200ms
- Python 调用 Rust: < 1ms

### 预期收益（小资金 100-500 USDT）

**保守场景**（无杠杆）:
- 月化收益: 8-15%

**激进场景**（2-3倍杠杆）:
- 月化收益: 20-50%
- ⚠️ 风险: 爆仓风险增加，需严格止损

---

## 风险提示

⚠️ **重要警告**:

1. **这是教育项目**: 用于学习 Rust/Python 混合开发和量化交易策略
2. **投资有风险**: 加密货币交易存在极高风险，可能导致全部本金损失
3. **先测试后实盘**: 务必在测试网充分测试后，再用小额资金实盘
4. **杠杆风险**: 使用杠杆可能导致快速爆仓
5. **技术风险**: 代码 bug、网络延迟、API 限速等可能造成损失

**建议**:
- 从测试网开始
- 小额资金（10-50 USDT）测试
- 不使用杠杆或低杠杆（2-3倍）
- 设置严格止损

---

## 贡献指南

### 代码风格

**Rust**:
- 使用 `rustfmt` 格式化代码
- 使用 `clippy` 检查代码质量
- 遵循 [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)

**Python**:
- 遵循 PEP 8 规范
- 使用类型提示（Type Hints）
- 使用 `black` 格式化代码
- 使用 `pylint` 检查代码质量

### 提交规范

```
<type>(<scope>): <subject>

[Agent X] feat(rest-client): 实现订单下单功能
[Agent Y] fix(websocket): 修复重连逻辑
[Coordinator] docs(interfaces): 更新接口文档
```

**类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 重构
- `perf`: 性能优化

---

## 常见问题 (FAQ)

### Q: 如何调试 Rust 代码？

A: 使用 VSCode 的 `rust-analyzer` 插件，配合 `lldb` 调试器。

### Q: Python 无法导入 Rust 模块？

A: 确保运行了 `maturin develop` 并且在正确的虚拟环境中。

### Q: 如何获取币安 API 密钥？

A: 登录币安官网 → 账户 → API 管理 → 创建 API Key（仅需要"读取"和"现货交易"权限）

### Q: 测试网 API 地址？

A: `https://testnet.binance.vision` （无需真实资金）

---

## 资源链接

- **币安 API 文档**: https://binance-docs.github.io/apidocs/spot/en/
- **Rust 官方文档**: https://doc.rust-lang.org/
- **PyO3 文档**: https://pyo3.rs/
- **Tokio 文档**: https://tokio.rs/

---

## 许可证

MIT License

---

## 联系方式

- **项目负责人**: 总指挥 Agent
- **问题反馈**: 提交 GitHub Issues
- **技术讨论**: 项目 Discussions

---

**祝各位 Agent 开发顺利！ 🚀**

# 快速启动指南

本文档帮助各 Agent 快速开始开发工作。

## 环境准备

### 1. 安装 Rust

```bash
# Windows
# 访问 https://rustup.rs/ 下载安装器

# Linux/Mac
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 验证安装
rustc --version  # 应该 >= 1.75
cargo --version
```

### 2. 安装 Python

```bash
# 确保 Python 3.10+
python --version

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. 安装 Maturin (用于 Rust-Python 绑定)

```bash
pip install maturin
```

## 项目结构概览

```
binance-arbitrage-bot/
├── rust-core/              # Rust 核心引擎 (Agent 1, 2, 3)
│   ├── src/
│   │   ├── lib.rs         # PyO3 绑定入口 (Agent 3)
│   │   ├── binance/       # 币安 API (Agent 1)
│   │   └── engine/        # 交易引擎 (Agent 2)
│   ├── Cargo.toml         # 已配置好所有依赖
│   └── pyproject.toml     # Maturin 配置
│
├── python-strategy/        # Python 策略层 (Agent 4, 5, 6)
│   ├── strategies/        # 策略 (Agent 4, 5)
│   ├── risk_management/   # 风险管理 (Agent 4)
│   ├── monitor/           # 监控 (Agent 6)
│   ├── backtest/          # 回测 (Agent 6)
│   ├── config.py          # 配置加载 (Agent 4)
│   ├── main.py            # 主程序 (Agent 6)
│   └── requirements.txt   # 已配置好所有依赖
│
├── config/
│   └── config.example.yaml  # 配置模板
│
└── docs/
    └── interfaces.md      # **接口规范 - 必读!**
```

## Agent 1: Rust 币安 API 客户端

### 开始开发

1. 阅读接口规范: [`docs/interfaces.md#1.1`](interfaces.md) 和 [`docs/interfaces.md#1.2`](interfaces.md)
2. 实现文件:
   - `rust-core/src/binance/rest_client.rs`
   - `rust-core/src/binance/websocket.rs`
   - `rust-core/src/binance/types.rs`

### 编译和测试

```bash
cd rust-core

# 开发模式编译
cargo build

# 运行测试
cargo test

# 代码检查
cargo clippy
```

### 验收标准

- [ ] REST API 所有端点通过单元测试
- [ ] WebSocket 能持续运行 1 小时不断线
- [ ] 速率限制自动处理（429 错误重试）
- [ ] 代码覆盖率 > 80%

---

## Agent 2: Rust 交易引擎

### 开始开发

1. 阅读接口规范: [`docs/interfaces.md#1.3-1.5`](interfaces.md)
2. 实现文件:
   - `rust-core/src/engine/order_executor.rs`
   - `rust-core/src/engine/price_monitor.rs`
   - `rust-core/src/engine/rate_limiter.rs`

### 依赖 Agent 1

**重要**: 你的代码依赖 Agent 1 的 `BinanceRestClient` 和 `BinanceWebSocket`。在 Agent 1 完成前，你可以创建 mock 对象进行开发。

### 编译和测试

```bash
cd rust-core
cargo build
cargo test
```

### 验收标准

- [ ] 订单执行延迟 < 100ms
- [ ] 价格监控器能同时处理 20+ 交易对
- [ ] 三角套利机会检测准确率 > 95%
- [ ] 压力测试：1000 次连续下单无失败

---

## Agent 3: PyO3 绑定层

### 开始开发

1. 阅读接口规范: [`docs/interfaces.md#1.6`](interfaces.md)
2. 主要文件:
   - `rust-core/src/lib.rs` (已有骨架代码)

### 依赖 Agent 1 和 2

**关键路径**: 你的工作是连接 Rust 和 Python 的桥梁。Agent 4/5/6 必须等待你完成才能测试 Python 代码。

### 编译 Python 模块

```bash
cd rust-core

# 开发模式（快速编译，可调试）
maturin develop

# 发布模式（性能优化）
maturin build --release
```

### 测试 Python 导入

```python
# 在 Python 中测试
from binance_rust_py import BinanceEngine

engine = BinanceEngine(api_key="test", api_secret="test", testnet=True)
print("导入成功!")
```

### 验收标准

- [ ] `maturin develop` 成功编译
- [ ] Python 能正常导入和调用所有方法
- [ ] 类型提示完整，IDE 自动补全正常
- [ ] 性能测试：Python 调用 Rust 开销 < 1ms

---

## Agent 4: Python 三角套利策略

### 开始开发

1. 阅读接口规范: [`docs/interfaces.md#2.2-2.3`](interfaces.md)
2. 实现文件:
   - `python-strategy/strategies/triangular_arbitrage.py`
   - `python-strategy/risk_management/position_manager.py`
   - `python-strategy/risk_management/stop_loss.py`
   - `python-strategy/config.py`

### 依赖 Agent 3

**前置条件**: Agent 3 完成 PyO3 绑定后，你才能真正测试代码。在此之前，可以创建 mock 对象开发。

### 安装依赖

```bash
cd python-strategy
pip install -r requirements.txt
```

### 测试

```bash
pytest tests/ --cov=strategies --cov=risk_management
```

### 验收标准

- [ ] 能正确生成所有可能的三角路径
- [ ] 风险控制参数生效
- [ ] 模拟运行 24 小时无错误
- [ ] 回测收益率符合预期

---

## Agent 5: Python 资金费率套利策略

### 开始开发

1. 阅读接口规范: [`docs/interfaces.md#2.4-2.5`](interfaces.md)
2. 实现文件:
   - `python-strategy/strategies/funding_rate.py`
   - `python-strategy/strategies/hybrid.py`

### 依赖 Agent 3 和 4

你的混合策略需要调用 Agent 4 的三角套利策略。

### 安装依赖

```bash
cd python-strategy
pip install -r requirements.txt
```

### 验收标准

- [ ] 能正确获取资金费率
- [ ] 对冲仓位数量精确匹配
- [ ] 爆仓监控实时预警
- [ ] 回测年化收益 > 20%

---

## Agent 6: Python 监控和可视化

### 开始开发

1. 阅读接口规范: [`docs/interfaces.md#2.6-2.8`](interfaces.md)
2. 实现文件:
   - `python-strategy/monitor/dashboard.py`
   - `python-strategy/monitor/logger.py`
   - `python-strategy/backtest/engine.py`
   - `python-strategy/backtest/visualization.py`
   - `python-strategy/main.py`

### 运行主程序

```bash
cd python-strategy

# 测试网运行
python main.py --testnet

# 回测模式
python main.py --backtest
```

### 验收标准

- [ ] 监控面板每秒刷新数据
- [ ] 日志文件正常轮转
- [ ] 回测结果与实盘对比误差 < 5%
- [ ] 可视化图表清晰易读

---

## 通用开发规范

### 代码风格

**Rust**:
```bash
# 格式化代码
cargo fmt

# 代码检查
cargo clippy
```

**Python**:
```bash
# 格式化代码
black python-strategy/

# 类型检查
mypy python-strategy/

# 代码检查
pylint python-strategy/
```

### 提交规范

```bash
# 创建功能分支
git checkout -b feature/agent-X-module-name

# 提交代码
git add .
git commit -m "[Agent X] feat(module): 实现某某功能"

# 推送
git push origin feature/agent-X-module-name
```

### 提交消息格式

```
[Agent X] <type>(<scope>): <subject>

类型 (type):
- feat: 新功能
- fix: Bug 修复
- docs: 文档更新
- test: 测试相关
- refactor: 重构
- perf: 性能优化
```

---

## 常见问题

### Q: Rust 编译报错找不到某个 crate

A: 运行 `cargo update` 更新依赖，确保网络畅通。

### Q: Python 无法导入 binance_rust_py

A: 确保运行了 `cd rust-core && maturin develop`，并且在正确的虚拟环境中。

### Q: 如何获取币安 API 密钥？

A:
1. 登录币安官网
2. 账户 → API 管理 → 创建 API Key
3. 仅勾选"读取"和"现货交易"权限
4. **先在测试网测试**: `https://testnet.binance.vision`

### Q: 我的模块依赖其他 Agent 的代码怎么办？

A:
1. 先阅读 `docs/interfaces.md` 了解接口定义
2. 创建 mock 对象进行独立开发
3. 其他 Agent 完成后，替换 mock 对象为真实实现

---

## 获取帮助

- **接口疑问**: 查看 [`docs/interfaces.md`](interfaces.md)
- **任务详情**: 查看 [`README.md`](../README.md)
- **Bug 报告**: 提交 GitHub Issues

---

**祝开发顺利! 🚀**

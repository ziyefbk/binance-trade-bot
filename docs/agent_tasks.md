# Agent 任务分配文档

本文档详细列出各 Agent 的具体任务、交付物和验收标准。

## 项目依赖关系图

```
         总指挥 Agent (Coordinator)
                 │
         ┌───────┴───────┐
         │  项目初始化    │
         │  接口定义      │
         │  集成测试      │
         └───────┬───────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│Agent 1│   │Agent 2│   │Agent 3│
│API客户│   │交易引擎│   │PyO3绑│
│  端   │   │      │   │  定   │ ← **关键路径**
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └───────┬───┴───────┬───┘
            │           │
    ┌───────┴───┬───────┴───┬───────┐
    │           │           │       │
┌───▼───┐   ┌──▼───┐   ┌───▼──┐   │
│Agent 4│   │Agent 5│   │Agent │   │
│三角套利│   │资金费率│   │  6   │   │
│      │   │  套利 │   │监控回测│   │
└───────┘   └───────┘   └──────┘   │
                                   │
                        ┌──────────▼────────┐
                        │   最终集成测试     │
                        │   (Coordinator)    │
                        └───────────────────┘
```

## Agent 任务清单

### 总指挥 Agent (Coordinator Agent)

**状态**: ✅ 已完成初始化

**职责**:
1. ✅ 创建项目目录结构
2. ✅ 定义接口规范文档 (`docs/interfaces.md`)
3. ✅ 创建项目骨架文件
4. ⏳ 协调各模块集成
5. ⏳ 代码审查
6. ⏳ 集成测试
7. ⏳ 部署和验证

**已完成工作**:
- 项目目录结构
- 接口规范文档 (773行)
- README.md
- Rust 项目骨架 (Cargo.toml, pyproject.toml, lib.rs)
- Python 项目骨架 (requirements.txt, 所有模块框架)
- 配置文件模板
- Git 仓库初始化

**下一步**:
- 等待各 Agent 完成开发
- 进行代码审查
- 执行集成测试

---

### Agent 1: Rust 币安 API 客户端开发

**优先级**: 🔴 高（其他 Agent 依赖）

**时间估算**: 第 1-3 天

**交付文件**:
- [x] `rust-core/src/binance/mod.rs` (已创建骨架)
- [ ] `rust-core/src/binance/rest_client.rs` (待实现)
- [ ] `rust-core/src/binance/websocket.rs` (待实现)
- [ ] `rust-core/src/binance/types.rs` (待实现)

**核心任务**:

#### 1.1 REST API 客户端
- [ ] 实现 HMAC-SHA256 签名算法
- [ ] 实现账户信息查询 (`/api/v3/account`)
- [ ] 实现交易对信息查询 (`/api/v3/exchangeInfo`)
- [ ] 实现下市价单 (`/api/v3/order` POST)
- [ ] 实现下限价单 (`/api/v3/order` POST)
- [ ] 实现查询订单状态 (`/api/v3/order` GET)
- [ ] 实现取消订单 (`/api/v3/order` DELETE)
- [ ] 实现获取当前价格 (`/api/v3/ticker/price`)
- [ ] 实现速率限制检测（解析 `X-MBX-USED-WEIGHT-1m` 响应头）
- [ ] 实现 429 错误自动重试

#### 1.2 WebSocket 客户端
- [ ] 实现 WebSocket 连接建立
- [ ] 实现深度行情流订阅 (`depth@100ms`)
- [ ] 实现成交流订阅 (`trade`)
- [ ] 实现 K 线流订阅 (`kline_1m`)
- [ ] 实现用户数据流订阅 (`userData`)
- [ ] 实现自动重连机制（断线后 5 秒重连）
- [ ] 实现心跳保持（Ping/Pong）
- [ ] 实现优雅关闭

#### 1.3 数据类型定义
- [ ] 定义 `AccountInfo`, `Balance`
- [ ] 定义 `OrderResponse`, `OrderStatus`
- [ ] 定义 `WebSocketMessage` 枚举
- [ ] 定义 `BinanceError` 错误类型
- [ ] 实现 serde 序列化/反序列化

**参考资料**:
- 币安 API 文档: https://binance-docs.github.io/apidocs/spot/en/
- 接口规范: [`docs/interfaces.md#1.1-1.2`](interfaces.md)

**验收标准**:
- [ ] 所有 REST API 端点通过单元测试
- [ ] WebSocket 能持续运行 1 小时不断线
- [ ] 速率限制自动处理（429 错误重试）
- [ ] 代码覆盖率 > 80%
- [ ] `cargo clippy` 无警告
- [ ] 通过 Coordinator 代码审查

---

### Agent 2: Rust 交易引擎开发

**优先级**: 🔴 高（Agent 3 依赖）

**时间估算**: 第 1-3 天（可与 Agent 1 并行）

**交付文件**:
- [x] `rust-core/src/engine/mod.rs` (已创建骨架)
- [ ] `rust-core/src/engine/order_executor.rs` (待实现)
- [ ] `rust-core/src/engine/price_monitor.rs` (待实现)
- [ ] `rust-core/src/engine/rate_limiter.rs` (待实现)

**核心任务**:

#### 2.1 订单执行引擎
- [ ] 实现单个订单执行 (`execute_order`)
- [ ] 实现三角套利原子执行 (`execute_triangular_arbitrage`)
  - 三个订单必须快速连续执行
  - 任何一个失败则回滚
  - 记录执行时间（目标 < 150ms）
- [ ] 实现批量订单执行 (`execute_batch`)
- [ ] 实现订单状态跟踪（HashMap 存储活跃订单）
- [ ] 实现失败重试逻辑（最多重试 3 次）
- [ ] 实现滑点计算和保护
- [ ] 实现取消所有订单 (`cancel_all`)

#### 2.2 价格监控器
- [ ] 实现 DashMap 价格缓存（线程安全）
- [ ] 实现 WebSocket 价格更新接收
- [ ] 实现 `get_price()` 快速查询（< 1ms）
- [ ] 实现 `get_depth()` 深度数据查询
- [ ] 实现三角套利机会扫描 (`scan_triangular_opportunities`)
  - 计算公式: `(1/price1) * price2 * price3 * (1-fee)^3 - 1`
  - 过滤利润 < 阈值的机会
- [ ] 实现价格异常检测（价格突变 > 10% 告警）
- [ ] 实现添加/移除交易对监控

#### 2.3 速率限制器
- [ ] 实现令牌桶算法
  - 初始化令牌桶（`max_tokens`, `refill_rate`）
  - 每秒补充 `refill_rate` 个令牌
- [ ] 实现 `try_acquire()` 非阻塞获取
- [ ] 实现 `acquire()` 阻塞获取（等待令牌可用）
- [ ] 实现 `available_tokens()` 查询
- [ ] 实现 `reset()` 重置

**参考资料**:
- 接口规范: [`docs/interfaces.md#1.3-1.5`](interfaces.md)
- DashMap 文档: https://docs.rs/dashmap/

**验收标准**:
- [ ] 订单执行延迟 < 100ms
- [ ] 三角套利全流程 < 150ms
- [ ] 价格监控器能同时处理 20+ 交易对
- [ ] 三角套利机会检测准确率 > 95%
- [ ] 压力测试：1000 次连续下单无失败
- [ ] 代码覆盖率 > 80%
- [ ] `cargo clippy` 无警告

---

### Agent 3: PyO3 绑定层开发

**优先级**: 🔴 极高（**关键路径** - Agent 4/5/6 依赖）

**时间估算**: 第 2-4 天

**前置依赖**: Agent 1 和 Agent 2 部分完成

**交付文件**:
- [x] `rust-core/src/lib.rs` (已创建骨架)
- [ ] `rust-core/Cargo.toml` (已配置，需确认)
- [ ] `rust-core/pyproject.toml` (已配置，需确认)
- [ ] `binance_rust_py.pyi` (Python 类型提示文件)

**核心任务**:

#### 3.1 Python 类包装
- [ ] 实现 `BinanceEngine` 主类
  - `__new__`: 初始化引擎
  - `start_market_data()`: 启动 WebSocket
  - `stop_market_data()`: 停止 WebSocket
  - `get_account_info()`: 获取账户信息
  - `get_price()`: 获取当前价格
  - `get_arbitrage_opportunities()`: 扫描套利机会
  - `execute_triangular_arbitrage()`: 执行三角套利
  - `place_order()`: 下单
  - `cancel_order()`: 取消订单
  - `get_balances()`: 获取余额

- [ ] 实现 Python 数据类
  - `PyArbitrageOpportunity`
  - `PyArbitrageResult`
  - `PyExecutionResult`
  - `PyBalance`
  - `PyAccountInfo`

#### 3.2 异步支持（可选）
- [ ] 使用 `pyo3-asyncio` 实现 asyncio 集成
- [ ] 异步方法暴露（如果需要）

#### 3.3 错误处理
- [ ] 将 Rust `BinanceError` 映射到 Python 异常
- [ ] 提供详细错误信息

#### 3.4 类型提示文件
- [ ] 创建 `binance_rust_py.pyi`
- [ ] 定义所有类的类型签名
- [ ] 确保 IDE 自动补全正常

**测试**:
```bash
cd rust-core
maturin develop

python -c "from binance_rust_py import BinanceEngine; print('OK')"
```

**参考资料**:
- PyO3 文档: https://pyo3.rs/
- 接口规范: [`docs/interfaces.md#1.6`](interfaces.md)

**验收标准**:
- [ ] `maturin develop` 成功编译
- [ ] Python 能正常导入和调用所有方法
- [ ] 类型提示完整，IDE 自动补全正常
- [ ] 性能测试：Python 调用 Rust 开销 < 1ms
- [ ] 错误处理正确（Rust 错误 → Python 异常）
- [ ] 通过 Coordinator 代码审查

---

### Agent 4: Python 三角套利策略开发

**优先级**: 🟡 中（依赖 Agent 3）

**时间估算**: 第 4-6 天

**前置依赖**: Agent 3 完成

**交付文件**:
- [x] `python-strategy/strategies/triangular_arbitrage.py` (已创建骨架)
- [x] `python-strategy/risk_management/position_manager.py` (已创建骨架)
- [x] `python-strategy/risk_management/stop_loss.py` (已创建骨架)
- [x] `python-strategy/config.py` (已创建骨架)
- [x] `config/config.example.yaml` (已创建)
- [ ] `tests/python_tests/test_triangular.py` (待创建)

**核心任务**:

#### 4.1 三角套利策略
- [ ] 实现 `generate_paths()` - 生成所有可能的三角路径
  - 输入: 交易对列表 `["BTCUSDT", "ETHBTC", "ETHUSDT"]`
  - 输出: 所有可能的三角路径（如 USDT→BTC→ETH→USDT）
- [ ] 实现 `scan_opportunities()` - 扫描套利机会
  - 调用 `engine.get_arbitrage_opportunities()`
  - 过滤利润 < 阈值的机会
- [ ] 实现 `execute()` - 执行套利
  - 风险检查
  - 调用 Rust 引擎执行
  - 记录执行结果
- [ ] 实现 `calculate_position_size()` - 计算仓位大小
  - 考虑总资金、最大单笔限制
  - 动态调整

#### 4.2 风险管理
- [ ] 实现 `PositionManager`
  - `get_total_balance_usdt()`: 获取总资金
  - `get_available_balance()`: 获取可用资金
  - `calculate_max_position_size()`: 计算最大仓位
  - `can_open_position()`: 检查是否可开仓
  - `get_all_positions()`: 获取所有持仓
- [ ] 实现 `StopLossManager`
  - `check_stop_loss()`: 检查止损
  - `execute_stop_loss()`: 执行止损

#### 4.3 配置加载
- [ ] 实现 `load_config()` - 加载 YAML 配置
- [ ] 定义配置数据类（已有骨架）

**参考资料**:
- 接口规范: [`docs/interfaces.md#2.2-2.3`](interfaces.md)

**验收标准**:
- [ ] 能正确生成所有可能的三角路径
- [ ] 风险控制参数生效
- [ ] 模拟运行 24 小时无错误
- [ ] 单元测试覆盖率 > 80%
- [ ] 回测收益率符合预期
- [ ] `pylint` 评分 > 8.0

---

### Agent 5: Python 资金费率套利策略开发

**优先级**: 🟡 中（依赖 Agent 3, 4）

**时间估算**: 第 4-6 天

**前置依赖**: Agent 3 完成，Agent 4 部分完成

**交付文件**:
- [x] `python-strategy/strategies/funding_rate.py` (已创建骨架)
- [x] `python-strategy/strategies/hybrid.py` (已创建骨架)
- [ ] `python-strategy/utils/leverage_calculator.py` (待创建)
- [ ] `python-strategy/utils/liquidation_monitor.py` (待创建)
- [ ] `tests/python_tests/test_funding_rate.py` (待创建)

**核心任务**:

#### 5.1 资金费率套利
- [ ] 实现 `get_current_rates()` - 获取资金费率
  - 调用币安 `/fapi/v1/premiumIndex` API
  - 解析费率数据
- [ ] 实现 `find_opportunities()` - 寻找机会
  - 过滤费率 > 阈值的交易对
  - 计算预期收益
- [ ] 实现 `open_position()` - 开仓
  - 现货买入
  - 合约做空（相同数量）
  - 确保对冲精确
- [ ] 实现 `close_position()` - 平仓
  - 现货卖出
  - 合约平空
- [ ] 实现 `monitor_positions()` - 监控持仓
  - 检查保证金率
  - 爆仓预警（< 30%）

#### 5.2 混合策略协调器
- [ ] 实现 `allocate_capital()` - 资金分配
  - 60% 资金费率, 40% 三角套利（默认）
- [ ] 实现 `run()` - 主循环
  - 同时运行两种策略
  - 协调资金分配
- [ ] 实现 `rebalance()` - 再平衡
  - 根据收益动态调整比例

#### 5.3 工具函数
- [ ] 实现 `leverage_calculator.py` - 杠杆计算
- [ ] 实现 `liquidation_monitor.py` - 爆仓监控

**参考资料**:
- 接口规范: [`docs/interfaces.md#2.4-2.5`](interfaces.md)
- 币安合约 API: https://binance-docs.github.io/apidocs/futures/en/

**验收标准**:
- [ ] 能正确获取资金费率
- [ ] 对冲仓位数量精确匹配
- [ ] 爆仓监控实时预警
- [ ] 回测年化收益 > 20%
- [ ] 单元测试覆盖率 > 80%
- [ ] `pylint` 评分 > 8.0

---

### Agent 6: Python 监控和可视化开发

**优先级**: 🟢 低（独立模块）

**时间估算**: 第 5-7 天

**前置依赖**: Agent 3 完成

**交付文件**:
- [x] `python-strategy/monitor/dashboard.py` (已创建骨架)
- [x] `python-strategy/monitor/logger.py` (已创建)
- [x] `python-strategy/backtest/engine.py` (已创建骨架)
- [x] `python-strategy/backtest/visualization.py` (已创建骨架)
- [x] `python-strategy/main.py` (已创建骨架)
- [ ] `tests/python_tests/test_backtest.py` (待创建)

**核心任务**:

#### 6.1 实时监控面板
- [ ] 实现 `Dashboard` 类
  - 使用 `rich` 库创建终端 UI
  - 实时显示：总资金、今日收益、订单数、成功率
  - 每秒刷新数据
- [ ] 实现 `_create_table()` - 创建表格

#### 6.2 日志系统
- [ ] 完善 `TradingLogger` (已有基础代码)
  - 文件轮转（10MB 自动切分）
  - 不同日志级别（DEBUG/INFO/WARN/ERROR）
  - 结构化日志

#### 6.3 回测引擎
- [ ] 实现 `load_historical_data()` - 加载历史数据
  - 从币安下载 K 线数据
  - 存储为 CSV 文件
- [ ] 实现 `run()` - 运行回测
  - 模拟策略执行
  - 计算收益
- [ ] 计算性能指标:
  - 夏普比率
  - 最大回撤
  - 胜率
  - 盈亏比

#### 6.4 数据可视化
- [ ] 实现 `plot_equity_curve()` - 资金曲线
- [ ] 实现 `plot_drawdown()` - 回撤曲线
- [ ] 实现 `plot_trade_distribution()` - 交易分布

#### 6.5 主程序入口
- [ ] 完善 `main.py` (已有骨架)
  - 命令行参数解析
  - 配置加载
  - 引擎初始化
  - 策略运行
  - 优雅关闭（Ctrl+C）

**参考资料**:
- 接口规范: [`docs/interfaces.md#2.6-2.8`](interfaces.md)
- Rich 文档: https://rich.readthedocs.io/

**验收标准**:
- [ ] 监控面板每秒刷新数据
- [ ] 日志文件正常轮转
- [ ] 回测结果与实盘对比误差 < 5%
- [ ] 可视化图表清晰易读
- [ ] 主程序能正常启动和停止
- [ ] `pylint` 评分 > 8.0

---

## 集成测试清单 (Coordinator Agent)

所有 Agent 完成后，Coordinator 执行以下测试:

### 单元测试
- [ ] Rust: `cd rust-core && cargo test`
- [ ] Python: `cd python-strategy && pytest tests/ --cov`

### 集成测试
- [ ] REST API 调用正常（测试网）
- [ ] WebSocket 持续运行稳定（1 小时）
- [ ] 三角套利机会检测准确
- [ ] 订单执行成功率 > 95%
- [ ] 资金费率套利对冲准确
- [ ] 监控面板数据正确
- [ ] 回测结果合理

### 性能测试
- [ ] WebSocket 延迟 < 50ms
- [ ] 订单执行延迟 < 100ms
- [ ] 三角套利全流程 < 200ms
- [ ] Python 调用 Rust < 1ms

### 稳定性测试
- [ ] 7x24 小时运行无崩溃
- [ ] 内存泄漏测试
- [ ] 异常恢复测试

---

## 开发时间表

| 阶段 | 时间 | 负责人 | 状态 |
|------|------|--------|------|
| 项目初始化 | 第 1 天 | Coordinator | ✅ 已完成 |
| Rust 核心开发 | 第 1-3 天 | Agent 1 + 2 | ⏳ 待开始 |
| PyO3 绑定 | 第 2-4 天 | Agent 3 | ⏳ 待开始 |
| Python 策略（三角） | 第 4-6 天 | Agent 4 | ⏳ 待开始 |
| Python 策略（资金费率） | 第 4-6 天 | Agent 5 | ⏳ 待开始 |
| 监控系统 | 第 5-7 天 | Agent 6 | ⏳ 待开始 |
| 集成测试 | 第 7-8 天 | Coordinator | ⏳ 待开始 |
| 部署验证 | 第 9-10 天 | Coordinator | ⏳ 待开始 |

**总计**: 10 个工作日（约 2 周）

---

## 联系方式

- **总指挥 Agent**: 负责协调和集成
- **问题反馈**: GitHub Issues
- **技术讨论**: 项目 Discussions

---

**祝各位 Agent 开发顺利! 🚀**

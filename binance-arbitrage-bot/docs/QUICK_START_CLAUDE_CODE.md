# Claude Code 快速设置指南 - C++ 交易机器人项目

## ⚡ 5 分钟快速设置

### Step 1: 复制必需的 Agents（1 分钟）

```bash
cd binance-arbitrage-bot
mkdir -p .claude/agents

# 从 everything-claude-code 复制关键 agents
cp ../everything-claude-code/agents/architect.md .claude/agents/
cp ../everything-claude-code/agents/planner.md .claude/agents/
cp ../everything-claude-code/agents/code-reviewer.md .claude/agents/
cp ../everything-claude-code/agents/tdd-guide.md .claude/agents/
cp ../everything-claude-code/agents/build-error-resolver.md .claude/agents/
cp ../everything-claude-code/agents/security-reviewer.md .claude/agents/
```

---

### Step 2: 复制必需的 Skills（1 分钟）

```bash
mkdir -p .claude/skills

# 复制关键 skills
cp -r ../everything-claude-code/skills/coding-standards .claude/skills/
cp -r ../everything-claude-code/skills/tdd-workflow .claude/skills/
cp -r ../everything-claude-code/skills/security-review .claude/skills/
cp -r ../everything-claude-code/skills/backend-patterns .claude/skills/
```

---

### Step 3: 配置 Project-Level CLAUDE.md（1 分钟）

在 `binance-arbitrage-bot/.claude.json` 中配置：

```json
{
  "disabledMcpServers": [],
  "preferences": {
    "model": "claude-sonnet-4-5",
    "context": {
      "type": "file",
      "path": "./.claude/context.md"
    }
  }
}
```

---

### Step 4: 配置 GitHub MCP（1 分钟）

编辑 `~/.claude.json`：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

> **如何获取 GitHub Token**:
> 1. 访问 https://github.com/settings/tokens
> 2. 点击 "Generate new token (classic)"
> 3. 选择权限: `repo`, `workflow`, `admin:org_hook`
> 4. 复制 token 到上面的配置

---

### Step 5: 复制 Rules（1 分钟）

```bash
# 复制到用户级规则目录
mkdir -p ~/.claude/rules
cp ../everything-claude-code/rules/security.md ~/.claude/rules/
cp ../everything-claude-code/rules/coding-style.md ~/.claude/rules/
cp ../everything-claude-code/rules/testing.md ~/.claude/rules/
```

---

## 🎯 立即使用的快速命令

### 规划新功能
```
/plan 实现 Boost.Asio 异步 WebSocket 客户端
```

### TDD 开发
```
/tdd 为 BinanceEngine 类编写单元测试
```

### 代码审查
```
/code-review cpp-core/src/engine.cpp
```

### 修复构建错误
```
/build-fix CMake 找不到 Boost
```

### 架构设计
使用 Claude Code 中的对话：
```
请使用 architect agent 设计 C++ 核心引擎的架构，
包括 WebSocket、REST API 和价格监控的交互方式
```

---

## 📂 推荐的项目结构

```
binance-arbitrage-bot/
├── .claude/                           # Claude Code 配置
│   ├── agents/                        # 复制的 agents
│   │   ├── architect.md
│   │   ├── planner.md
│   │   ├── code-reviewer.md
│   │   ├── tdd-guide.md
│   │   ├── security-reviewer.md
│   │   └── build-error-resolver.md
│   ├── skills/                        # 复制的 skills
│   │   ├── coding-standards/
│   │   ├── tdd-workflow/
│   │   ├── security-review/
│   │   └── backend-patterns/
│   ├── context.md                     # 项目上下文
│   └── .claude.json                   # 项目配置
│
├── cpp-core/                          # C++ 核心引擎
│   ├── include/
│   ├── src/
│   ├── tests/
│   ├── benchmarks/
│   └── CMakeLists.txt
│
├── python-strategy/                   # Python 策略层
├── python-bindings/                   # Python-C++ 绑定
├── docs/
│   ├── CLAUDE_CODE_RESOURCES.md       # 本文档
│   ├── QUANTITATIVE_INTERVIEW_STRATEGY.md
│   ├── RUST_VS_CPP_COMPARISON.md
│   ├── ARCHITECTURE.md                # 架构文档
│   ├── API_DESIGN.md                  # API 设计
│   └── DEPLOYMENT.md
└── config/
```

---

## 🔧 创建项目上下文文件

创建 `.claude/context.md`：

```markdown
# 币安套利交易机器人 - 项目上下文

## 项目目标
实现一个低延迟的 C++ 交易引擎，用于量化面试展示。

## 核心要求
- WebSocket 延迟 < 100µs
- 完整套利周期 < 1ms
- 无内存泄漏（RAII + 智能指针）
- 无数据竞争（原子操作 + 无锁数据结构）

## 技术栈
- C++17: 现代特性，智能指针，RAII
- Boost.Asio: 异步网络 I/O
- Boost.Beast: WebSocket 实现
- RapidJSON: 高性能 JSON 解析
- Google Test: 单元测试
- Google Benchmark: 性能测试

## 模块结构

### 1. Binance API 客户端
- **WebSocket**: 实时价格流（Boost.Beast）
- **REST API**: 订单执行（libcurl/Boost.Asio）
- **签名**: HMAC-SHA256 请求签名

### 2. 核心引擎
- **价格监控**: 原子操作的无锁缓存
- **订单执行**: 线程池 + 队列
- **速率限制**: 令牌桶算法

### 3. 风险管理
- **头寸管理**: 头寸大小限制
- **止损**: 自动平仓
- **监控**: 实时仪表板

## 设计原则
1. **性能优先**: 预分配、零拷贝、缓存友好
2. **安全优先**: 智能指针、原子操作、类型安全
3. **可测试性**: 依赖注入、分层架构
4. **可维护性**: 清晰的模块边界、充分的文档

## 开发工作流
1. **规划**: 使用 /plan 命令
2. **设计**: 使用 architect agent
3. **TDD**: 使用 /tdd 命令，确保 > 80% 覆盖率
4. **审查**: 使用 /code-review 和 security-reviewer
5. **优化**: 使用 Google Benchmark 和 perf

## 量化面试目标
- 展示现代 C++17 特性掌握
- 展示低延迟系统设计理解
- 展示多线程和无锁编程能力
- 展示完整的工程能力（测试、文档、基准）
```

---

## 💾 常用 Claude Code 工作流

### 工作流 1：实现一个新模块

```bash
# 1. 规划
/plan 实现 WebSocket 客户端，包括连接、订阅和重连逻辑

# 2. 输出
# - 步骤列表
# - 文件结构
# - 接口设计

# 3. 架构设计
"我要实现 WebSocket 客户端。使用 architect agent 帮我：
1. 设计类结构
2. 选择 Boost.Beast vs 自己实现的权衡
3. 错误处理策略
4. 测试策略"

# 4. TDD 开发
/tdd 为 WebSocketClient 编写单元测试

# 5. 编写代码
[根据测试编写实现]

# 6. 代码审查
/code-review cpp-core/src/websocket.cpp

# 7. 安全审查
"使用 security-reviewer agent 检查 WebSocket 实现的安全性"

# 8. 性能测试
"编写 Google Benchmark 基准测试并分析性能"
```

---

### 工作流 2：修复 Bug

```bash
# 1. 描述问题
"这是内存泄漏吗？错误信息：..."

# 2. 自动诊断
"使用 code-reviewer agent 分析这段代码"

# 3. 如果是构建错误
/build-fix CMake 链接错误：找不到 libboost_system

# 4. 修复后验证
/code-review 修复后的代码

# 5. 添加测试
/tdd 为这个 bug 添加单元测试
```

---

### 工作流 3：性能优化

```bash
# 1. 基准测试
"运行 Google Benchmark，测试 WebSocket 消息处理延迟"

# 2. 分析
"使用 code-reviewer agent，找出性能瓶颈"

# 3. 优化
[根据分析进行优化]

# 4. 重新基准测试
"验证优化效果，确保延迟 < 100µs"
```

---

## 📊 推荐的开发顺序

### 第 1 周：架构和框架
```
Day 1: 项目设置 + CMake 配置
Day 2-3: 架构设计（使用 architect agent）
Day 4-5: 基础类型定义（types.h）
Day 6-7: 项目框架和测试基础设施
```

### 第 2-3 周：核心实现
```
Week 2: Binance API 客户端
  - REST API 客户端（日 1-2）
  - WebSocket 客户端（日 3-4）
  - 签名和认证（日 5）

Week 3: 核心引擎
  - 价格监控（日 1-2）
  - 订单执行（日 3-4）
  - 风险管理（日 5）
```

### 第 4 周：集成、测试、优化
```
Day 1-2: Python 绑定
Day 3-4: 集成测试
Day 5: 性能优化和基准测试
```

---

## 🎯 在面试中使用

### 展示你的项目

```bash
# 1. 打开项目
git clone https://github.com/ziyefbk/binance-trade-bot.git
cd binance-trade-bot

# 2. 展示结构
tree cpp-core/
tree python-bindings/

# 3. 运行测试
cd cpp-core/build
cmake ..
cmake --build .
ctest --verbose

# 4. 运行基准测试
./benchmark_engine

# 5. 展示代码
# 打开几个关键文件讲解：
# - include/binance/engine.h
# - src/engine.cpp
# - tests/engine_test.cpp
```

### 回答常见问题

**Q: 为什么选择 C++？**
A: 交易系统需要极低的延迟和可预测的性能。C++ 提供：
- 零运行时开销的抽象
- 完全的内存控制
- 高效的并发机制

**Q: 如何处理并发？**
A: 使用以下技术：
- std::atomic<T> 用于价格缓存（无锁）
- std::thread + 线程池用于订单执行
- ThreadSanitizer 检测数据竞争

**Q: 性能指标如何？**
A: 使用 Google Benchmark 测试：
- WebSocket 消息处理: < 100µs
- 完整套利周期: < 1ms
- 内存分配: 0（热路径）

---

## ✅ 检查清单

- [ ] 复制了所有 agents 到 `.claude/agents/`
- [ ] 复制了关键 skills 到 `.claude/skills/`
- [ ] 配置了 `.claude.json`
- [ ] 配置了 `~/.claude.json` 的 MCP servers
- [ ] 创建了 `.claude/context.md`
- [ ] 复制了 rules 到 `~/.claude/rules/`
- [ ] 测试了 `/plan` 命令
- [ ] 测试了 `/tdd` 命令
- [ ] 创建了 `cpp-core` 项目结构
- [ ] 准备好开始开发！

---

## 🚀 现在开始

执行命令开始第一个规划：

```bash
cd binance-arbitrage-bot
/plan 实现 C++ WebSocket 客户端，支持 Binance API 实时价格流
```

或者让我帮你：

```
我已经准备好了，请帮我设计 C++ 核心引擎的架构。
```

祝你开发顺利！💪

# Everything Claude Code - 推荐配置用于 C++ 交易机器人开发

## 📚 资源概览

从 `everything-claude-code` 仓库中，我为你的 **C++ 币安套利交易机器人** 项目选择了最合适的资源。

---

## 🤖 推荐的 Agents（代理）

### 1. **Architect Agent** ⭐⭐⭐⭐⭐
**文件**: `agents/architect.md`

**用途**: 系统架构设计和技术决策

**为什么适合**:
- 帮助设计 C++ 核心引擎的架构
- 评估 Boost.Asio vs libcurl vs 原生实现
- 规划低延迟系统的权衡（性能 vs 可维护性）
- 创建架构决策记录（ADR）

**何时使用**:
```bash
# 在开始实现前
"请使用 architect agent 帮我设计 C++ WebSocket 客户端的架构"
```

**关键输出**: Architecture Decision Records (ADRs)

---

### 2. **Planner Agent** ⭐⭐⭐⭐⭐
**文件**: `agents/planner.md`

**用途**: 功能实现规划

**为什么适合**:
- 将大任务分解为小步骤
- 规划 C++ 模块的实现顺序
- 估算开发时间
- 识别依赖关系

**何时使用**:
```bash
# 在开始编码前
"请使用 planner agent 规划如何实现无锁价格监控器"
```

---

### 3. **TDD Guide Agent** ⭐⭐⭐⭐
**文件**: `agents/tdd-guide.md`

**用途**: 测试驱动开发指导

**为什么适合**:
- 确保 C++ 代码质量
- 编写 Google Test 单元测试
- 测试覆盖率 > 80%
- 防止内存泄漏和竞态条件

**何时使用**:
```bash
# 在编写每个模块时
"请使用 tdd-guide agent 帮我为 WebSocket 客户端编写测试"
```

---

### 4. **Code Reviewer Agent** ⭐⭐⭐⭐⭐
**文件**: `agents/code-reviewer.md`

**用途**: 代码质量和安全审查

**为什么适合**:
- 检查内存泄漏（智能指针使用）
- 检查并发安全（数据竞争）
- 检查性能瓶颈
- 确保现代 C++ 最佳实践

**何时使用**:
```bash
# 在完成模块后
"请使用 code-reviewer agent 审查我的 BinanceEngine 实现"
```

---

### 5. **Security Reviewer Agent** ⭐⭐⭐⭐
**文件**: `agents/security-reviewer.md`

**用途**: 安全漏洞分析

**为什么适合**:
- 检查 API 密钥安全
- 检查输入验证（防止注入）
- 检查密码学实现（HMAC-SHA256）
- 检查网络安全（SSL/TLS）

**何时使用**:
```bash
# 在集成 API 后
"请使用 security-reviewer agent 检查 REST API 客户端的安全性"
```

---

### 6. **Build Error Resolver Agent** ⭐⭐⭐⭐
**文件**: `agents/build-error-resolver.md`

**用途**: 解决构建和编译错误

**为什么适合**:
- 解决 CMake 配置问题
- 解决链接错误
- 解决依赖问题（Boost, OpenSSL）
- 跨平台编译问题

**何时使用**:
```bash
# 遇到编译错误时
"请使用 build-error-resolver agent 帮我解决这个链接错误"
```

---

## 🛠️ 推荐的 Skills（技能包）

### 1. **Coding Standards** ⭐⭐⭐⭐⭐
**文件**: `skills/coding-standards/skill.md`

**适用性**: 虽然针对 TypeScript，但原则通用

**C++ 适配要点**:
- ✅ KISS, DRY, YAGNI 原则
- ✅ 命名规范（变量、函数、类）
- ✅ 错误处理（try-catch）
- ✅ 注释最佳实践（解释 WHY 而非 WHAT）
- ✅ 文件组织结构

**推荐**: 创建一个 `cpp-coding-standards.md` 适配版本

---

### 2. **Backend Patterns** ⭐⭐⭐⭐
**文件**: `skills/backend-patterns/`

**为什么适合**:
- Repository Pattern（抽象数据访问）
- Service Layer（业务逻辑分离）
- Event-Driven Architecture（异步操作）

**C++ 适配**:
- 用于设计 Binance API 客户端
- 用于设计价格监控和订单执行的分层架构

---

### 3. **TDD Workflow** ⭐⭐⭐⭐⭐
**文件**: `skills/tdd-workflow/`

**为什么适合**:
- 红-绿-重构循环
- 测试先行开发
- 确保代码质量

**C++ 工具栈**:
- Google Test 单元测试
- Google Benchmark 性能测试
- AddressSanitizer 内存检测
- ThreadSanitizer 并发检测

---

### 4. **Security Review** ⭐⭐⭐⭐⭐
**文件**: `skills/security-review/`

**为什么关键**:
- 交易系统涉及资金安全
- API 密钥管理
- 网络安全（SSL/TLS）
- 输入验证

---

### 5. **Iterative Retrieval** ⭐⭐⭐⭐
**文件**: `skills/iterative-retrieval/`

**用途**: 渐进式上下文细化

**为什么有用**:
- 在大型 C++ 项目中逐步查找代码
- 避免一次性加载过多上下文
- 优化 token 使用

---

## 📋 推荐的 Commands（斜杠命令）

### 1. **/plan** ⭐⭐⭐⭐⭐
**文件**: `commands/plan.md`

**用途**: 快速生成实现计划

```bash
/plan 实现 Boost.Asio 异步 WebSocket 客户端
```

---

### 2. **/tdd** ⭐⭐⭐⭐⭐
**文件**: `commands/tdd.md`

**用途**: 测试驱动开发工作流

```bash
/tdd 为 PriceMonitor 类编写单元测试
```

---

### 3. **/code-review** ⭐⭐⭐⭐
**文件**: `commands/code-review.md`

**用途**: 快速代码审查

```bash
/code-review cpp-core/src/engine.cpp
```

---

### 4. **/build-fix** ⭐⭐⭐⭐
**文件**: `commands/build-fix.md`

**用途**: 修复构建错误

```bash
/build-fix cmake 链接错误
```

---

## 🔌 推荐的 MCP Servers

### 1. **GitHub MCP** ⭐⭐⭐⭐⭐
**配置**: `mcp-configs/mcp-servers.json`

**为什么必需**:
- 自动创建 PR
- 管理 Issues
- 查看提交历史

**配置**:
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN_HERE"
    }
  }
}
```

---

### 2. **Memory MCP** ⭐⭐⭐⭐
**为什么有用**:
- 跨会话保存上下文
- 记住架构决策
- 记住编码约定

**配置**:
```json
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

---

### 3. **Sequential Thinking MCP** ⭐⭐⭐⭐
**为什么有用**:
- 复杂问题的链式推理
- 架构设计思考过程
- 调试复杂错误

**配置**:
```json
{
  "sequential-thinking": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
  }
}
```

---

### 4. **Context7 MCP** ⭐⭐⭐⭐
**为什么有用**:
- 实时查询 Boost 文档
- 实时查询 C++ 标准库文档
- 实时查询 CMake 文档

**配置**:
```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@context7/mcp-server"]
  }
}
```

---

## 📝 推荐的 Rules（规则）

从 `rules/` 目录复制到 `~/.claude/rules/`：

### 1. **security.md** ⭐⭐⭐⭐⭐
- 强制安全检查
- API 密钥保护
- 输入验证

### 2. **coding-style.md** ⭐⭐⭐⭐
- 文件组织
- 命名规范
- 代码格式

### 3. **testing.md** ⭐⭐⭐⭐⭐
- TDD 要求
- 80% 测试覆盖率
- 性能基准测试

---

## 🎯 为 C++ 项目创建的自定义 Skills

基于 `everything-claude-code` 的模式，我建议创建以下自定义 skills：

### 1. **cpp-modern-practices.md**
```markdown
---
name: cpp-modern-practices
description: Modern C++17/20 best practices for low-latency trading systems
---

# Modern C++ Best Practices

## Smart Pointers
- Use unique_ptr for ownership
- Use shared_ptr for shared ownership
- Use weak_ptr to break cycles
- NEVER use raw new/delete

## RAII Pattern
- All resources in constructors
- All cleanup in destructors
- No manual cleanup needed

## Lock-Free Programming
- Use std::atomic for counters
- Use atomic_compare_exchange for updates
- Minimize mutex usage
- Prefer lock-free over mutex

## Move Semantics
- Use std::move for transfers
- Return by value (RVO)
- Pass by const& or &&

## Zero-Copy Techniques
- Use string_view for read-only strings
- Use span for array views
- Avoid unnecessary copies
```

---

### 2. **cpp-low-latency-patterns.md**
```markdown
---
name: cpp-low-latency-patterns
description: Patterns for microsecond-latency trading systems
---

# Low-Latency C++ Patterns

## Memory Pre-allocation
- Pre-allocate buffers at startup
- Use object pools
- Avoid allocations in hot paths

## Cache-Friendly Data Structures
- Struct-of-arrays > Array-of-structs
- Align data to cache lines
- Minimize padding

## Performance Measurement
- Use Google Benchmark
- Measure p50, p95, p99 latency
- Profile with perf/VTune
```

---

### 3. **binance-api-patterns.md**
```markdown
---
name: binance-api-patterns
description: Patterns for Binance API integration
---

# Binance API Integration

## REST API
- Sign requests with HMAC-SHA256
- Handle rate limits (1200/min)
- Retry with exponential backoff

## WebSocket
- Subscribe to ticker streams
- Handle reconnections
- Parse JSON efficiently (RapidJSON)

## Risk Management
- Validate all orders before sending
- Track position limits
- Monitor liquidation risk
```

---

## 🚀 使用建议

### 第 1 步：设置 MCP Servers

```bash
# 1. 编辑 ~/.claude.json
# 2. 添加以下 MCP servers:
{
  "mcpServers": {
    "github": { ... },      # GitHub 集成
    "memory": { ... },      # 记忆持久化
    "context7": { ... }     # 文档查询
  }
}
```

---

### 第 2 步：复制 Agents 到项目

```bash
cp everything-claude-code/agents/architect.md binance-arbitrage-bot/.claude/agents/
cp everything-claude-code/agents/planner.md binance-arbitrage-bot/.claude/agents/
cp everything-claude-code/agents/tdd-guide.md binance-arbitrage-bot/.claude/agents/
cp everything-claude-code/agents/code-reviewer.md binance-arbitrage-bot/.claude/agents/
```

---

### 第 3 步：复制 Skills

```bash
cp everything-claude-code/skills/coding-standards binance-arbitrage-bot/.claude/skills/
cp everything-claude-code/skills/tdd-workflow binance-arbitrage-bot/.claude/skills/
cp everything-claude-code/skills/security-review binance-arbitrage-bot/.claude/skills/
```

---

### 第 4 步：复制 Rules

```bash
cp everything-claude-code/rules/*.md ~/.claude/rules/
```

---

### 第 5 步：使用 Commands

在 Claude Code 中直接使用：

```bash
/plan 实现 C++ WebSocket 客户端
/tdd 为 PriceMonitor 编写测试
/code-review cpp-core/src/engine.cpp
```

---

## 📊 优先级推荐

| 资源 | 优先级 | 原因 |
|------|--------|------|
| **Architect Agent** | 🔴 必需 | 架构设计是基础 |
| **Code Reviewer** | 🔴 必需 | C++ 代码质量关键 |
| **TDD Workflow** | 🔴 必需 | 测试保证正确性 |
| **Security Review** | 🔴 必需 | 交易系统安全至关重要 |
| **GitHub MCP** | 🟡 推荐 | 自动化 Git 操作 |
| **Memory MCP** | 🟡 推荐 | 跨会话保存知识 |
| **Context7 MCP** | 🟢 可选 | 实时文档查询 |
| **Backend Patterns** | 🟡 推荐 | 架构模式参考 |

---

## 💡 工作流示例

### 场景 1：实现新功能

```bash
# Step 1: 规划
/plan 实现 Boost.Beast WebSocket 客户端

# Step 2: 架构设计
"使用 architect agent 设计 WebSocket 客户端架构"

# Step 3: TDD 开发
/tdd 编写 WebSocketClient 测试

# Step 4: 编写代码
[编写 C++ 代码]

# Step 5: 代码审查
/code-review cpp-core/src/websocket.cpp

# Step 6: 安全审查
"使用 security-reviewer agent 检查 WebSocket 安全性"
```

---

### 场景 2：修复构建错误

```bash
# Step 1: 快速修复
/build-fix CMake 找不到 Boost.Asio

# Step 2: 如果复杂
"使用 build-error-resolver agent 解决这个链接错误"
```

---

### 场景 3：面试前准备

```bash
# Step 1: 代码审查
/code-review 整个 cpp-core 目录

# Step 2: 性能报告
"生成性能基准测试报告"

# Step 3: 文档更新
"更新 README 和架构文档"
```

---

## 📚 学习资源

### 从 everything-claude-code 学习

1. **阅读指南**:
   - `the-shortform-guide.md` - 快速上手
   - `the-longform-guide.md` - 深入理解

2. **查看示例**:
   - `examples/CLAUDE.md` - 项目级配置
   - `examples/user-CLAUDE.md` - 用户级配置

3. **探索 Hooks**:
   - `hooks/memory-persistence/` - 会话持久化
   - `hooks/strategic-compact/` - 上下文压缩

---

## ✨ 总结

### 最小必需配置

1. ✅ **Agents**: architect, planner, code-reviewer, tdd-guide
2. ✅ **Skills**: coding-standards, tdd-workflow, security-review
3. ✅ **MCP**: GitHub
4. ✅ **Rules**: security.md, testing.md

### 推荐配置

在最小配置基础上添加：
1. ✅ **MCP**: memory, context7
2. ✅ **Agents**: security-reviewer, build-error-resolver
3. ✅ **Skills**: backend-patterns, iterative-retrieval

### 完整配置

所有上述 + 自定义 C++ skills

---

## 🎓 下一步

1. **立即行动**: 复制最小必需配置
2. **渐进增强**: 随项目发展添加更多资源
3. **持续优化**: 根据实际使用调整配置

---

**记住**: 不要一次性添加所有内容，从核心开始，逐步扩展！

# 快速部署指南

## Docker 部署完成准备

我已经为你创建了完整的 Docker 部署配置。以下是所有创建的文件：

### 📁 新增文件

1. **[Dockerfile](Dockerfile)** - 多阶段构建配置
2. **[docker-compose.yml](docker-compose.yml)** - Docker Compose 编排配置
3. **[.dockerignore](.dockerignore)** - Docker 构建忽略文件
4. **[.env.example](.env.example)** - 环境变量模板
5. **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - 详细 Docker 使用指南
6. **[start.sh](start.sh)** - Linux/Mac 快速启动脚本
7. **[start.bat](start.bat)** - Windows 快速启动脚本

---

## 🚀 快速开始（3 步）

### 步骤 1: 启动 Docker Desktop

在 Windows 上，请先启动 Docker Desktop 应用程序：
- 在开始菜单搜索 "Docker Desktop"
- 点击启动
- 等待 Docker 引擎完全启动（系统托盘图标显示绿色）

验证 Docker 已启动：
```bash
docker ps
# 应该返回容器列表（可能是空的），而不是错误
```

### 步骤 2: 构建镜像

在 Windows 上双击运行 `start.bat`，或在命令行中：

```bash
cd binance-arbitrage-bot

# 方式 1: 使用快速启动脚本（推荐）
start.bat

# 在菜单中选择 4) 构建镜像

# 方式 2: 直接命令
docker-compose build
```

构建时间：首次约 5-10 分钟（取决于网络速度）

### 步骤 3: 运行测试

```bash
# 方式 1: 使用快速启动脚本（推荐）
start.bat
# 在菜单中选择 1) 回测模式

# 方式 2: 直接命令
docker-compose up
```

---

## 📋 运行模式说明

### 1️⃣ 回测模式（最安全，推荐首次使用）

**特点**:
- ✅ 不需要 API 密钥
- ✅ 使用历史数据
- ✅ 完全安全，无资金风险
- ✅ 快速验证策略逻辑

**运行**:
```bash
# Windows
start.bat → 选择 1

# Linux/Mac
./start.sh → 选择 1

# 或直接命令
docker-compose up
```

### 2️⃣ 测试网模式（需要测试网 API）

**特点**:
- ⚠️ 需要币安测试网 API 密钥
- ✅ 使用虚拟资金
- ✅ 测试实时连接和订单执行
- ⚠️ 需要先配置 API 密钥

**获取测试网 API**:
1. 访问 https://testnet.binance.vision/
2. 注册并生成 API 密钥
3. 在 [config/config.yaml](config/config.yaml) 中配置

**运行**:
```bash
# Windows
start.bat → 选择 2

# 或直接命令
docker-compose run --rm binance-bot python main.py --testnet
```

### 3️⃣ 实盘模式（使用真实资金）

**特点**:
- ⚠️⚠️⚠️ 使用真实资金
- ⚠️ 需要实盘 API 密钥
- ⚠️ 建议先小额测试

**运行**:
```bash
# Windows
start.bat → 选择 3 → 确认 "yes"

# 或直接命令
docker-compose run --rm binance-bot python main.py --live
```

---

## ⚙️ 配置说明

### API 密钥配置

编辑 [config/config.yaml](config/config.yaml):

```yaml
binance:
  # 测试网 API（用于测试）
  testnet:
    api_key: "your_testnet_api_key"
    api_secret: "your_testnet_api_secret"
    base_url: "https://testnet.binance.vision"

  # 实盘 API（谨慎使用）
  mainnet:
    api_key: "your_real_api_key"
    api_secret: "your_real_api_secret"
    base_url: "https://api.binance.com"

strategy:
  # 策略选择: triangular, funding_rate, hybrid
  type: "triangular"

  # 资金配置
  capital:
    total: 1000  # USDT
    max_position_size: 0.3  # 单笔最大 30%

  # 风险管理
  risk:
    max_drawdown: 0.05  # 最大回撤 5%
    stop_loss: 0.02     # 止损 2%
```

---

## 🔧 常用命令

### Windows 用户（推荐使用 start.bat）

```bash
# 启动快速菜单
start.bat

# 菜单选项：
# 1) 回测模式
# 2) 测试网模式
# 3) 实盘模式
# 4) 构建镜像
# 5) 查看日志
# 6) 停止容器
# 7) 后台运行
# 8) 查看状态
```

### 直接使用 Docker 命令

```bash
# 构建镜像
docker-compose build

# 前台运行（Ctrl+C 停止）
docker-compose up

# 后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down

# 查看容器状态
docker-compose ps

# 进入容器调试
docker-compose exec binance-bot bash
```

---

## 📊 监控和调试

### 查看实时日志

```bash
# 方式 1: Docker Compose
docker-compose logs -f

# 方式 2: 宿主机日志文件
# 日志会同步到: ./logs/ 目录
tail -f logs/bot.log
```

### 查看资源使用

```bash
# 实时监控
docker stats binance-arbitrage-bot

# 或使用 start.bat 选项 8
```

### 调试模式

```bash
# 进入容器内部
docker-compose exec binance-bot bash

# 在容器内手动运行
cd /app/python-strategy
python main.py --backtest
```

---

## 🛠️ 故障排查

### 问题 1: Docker Desktop 未启动

**错误信息**:
```
error during connect: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

**解决方法**:
1. 启动 Docker Desktop 应用程序
2. 等待状态图标变为绿色
3. 运行 `docker ps` 验证

### 问题 2: 端口冲突

**错误信息**:
```
Bind for 0.0.0.0:XXXX failed: port is already allocated
```

**解决方法**:
1. 检查并停止占用端口的程序
2. 或修改 docker-compose.yml 中的端口映射

### 问题 3: 镜像构建失败

**解决方法**:
```bash
# 清理缓存重新构建
docker builder prune
docker-compose build --no-cache
```

### 问题 4: 配置文件错误

**解决方法**:
```bash
# 验证 YAML 语法
docker-compose config

# 重新从模板复制
cp config/config.example.yaml config/config.yaml
```

---

## 📈 性能优化建议

### 资源限制

在 [docker-compose.yml](docker-compose.yml) 中已配置：

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # 调整为你的 CPU 核心数
      memory: 2G       # 根据可用内存调整
```

### 网络优化

如果访问 PyPI/Cargo 较慢，可以配置国内镜像：

**Python (pip.conf)**:
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

**Rust (config.toml)**:
```toml
[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "https://mirrors.ustc.edu.cn/crates.io-index"
```

---

## ✅ 验收检查清单

完成以下检查，确保部署成功：

- [ ] Docker Desktop 已启动并运行
- [ ] 镜像构建成功（`docker images | grep binance`）
- [ ] 配置文件已准备（`config/config.yaml`）
- [ ] 回测模式运行成功（`start.bat` → 1）
- [ ] 日志输出正常（`logs/` 目录有日志文件）
- [ ] 容器可以正常停止和重启

---

## 🎯 推荐流程

### 第一次使用（学习和验证）

1. ✅ **运行回测模式** - 验证策略逻辑
2. ✅ **分析回测结果** - 查看收益、回撤等指标
3. ✅ **调整参数** - 优化策略配置
4. ✅ **重复回测** - 直到满意

### 进入测试网（实战演练）

5. ⚠️ **配置测试网 API**
6. ⚠️ **运行测试网模式** - 验证实时连接
7. ⚠️ **观察 24-48 小时** - 确认稳定性
8. ⚠️ **检查日志和监控**

### 实盘测试（谨慎阶段）

9. ⚠️⚠️ **配置实盘 API（只读权限）**
10. ⚠️⚠️ **小额测试（10-20 USDT）**
11. ⚠️⚠️ **运行 1-2 周观察**
12. ⚠️⚠️ **逐步增加资金**

---

## 📚 相关文档

- [README.md](README.md) - 项目总览
- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - 详细 Docker 指南
- [COMPILE_GUIDE.md](COMPILE_GUIDE.md) - 编译指南
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - 快速开始
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结

---

## 🆘 获取帮助

遇到问题？
1. 查看 [DOCKER_GUIDE.md](DOCKER_GUIDE.md) 故障排查部分
2. 检查日志文件：`logs/bot.log`
3. 查看容器状态：`docker-compose ps`
4. 查看容器日志：`docker-compose logs -f`

---

## 下一步

**现在你可以**:

1. 启动 Docker Desktop
2. 运行 `start.bat`（Windows）或 `./start.sh`（Linux/Mac）
3. 选择 4 构建镜像
4. 选择 1 运行回测模式
5. 查看结果和日志

祝你使用愉快！🚀

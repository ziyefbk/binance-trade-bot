# Docker 部署指南

本指南介绍如何使用 Docker 运行币安套利机器人。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+

## 快速开始

### 1. 准备配置文件

```bash
# 复制配置模板
cd binance-arbitrage-bot
cp config/config.example.yaml config/config.yaml

# 编辑配置文件，填入你的 API 密钥
# 注意：回测模式不需要真实的 API 密钥
nano config/config.yaml  # 或使用你喜欢的编辑器
```

### 2. 创建必要的目录

```bash
# 创建日志和数据目录
mkdir -p logs data
```

### 3. 构建 Docker 镜像

```bash
# 构建镜像（首次运行或代码更新后需要）
docker-compose build

# 或使用 Docker 命令
docker build -t binance-arbitrage-bot:latest .
```

### 4. 运行容器

#### 方式 1: 使用 docker-compose（推荐）

```bash
# 回测模式（默认，最安全）
docker-compose up

# 后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

#### 方式 2: 使用 Docker 命令

```bash
# 回测模式
docker run --rm \
  -v $(pwd)/config/config.yaml:/app/config/config.yaml:ro \
  -v $(pwd)/logs:/app/logs \
  binance-arbitrage-bot:latest \
  python main.py --backtest

# 测试网模式
docker run --rm \
  -v $(pwd)/config/config.yaml:/app/config/config.yaml:ro \
  -v $(pwd)/logs:/app/logs \
  binance-arbitrage-bot:latest \
  python main.py --testnet

# 实盘模式（谨慎使用！）
docker run --rm \
  -v $(pwd)/config/config.yaml:/app/config/config.yaml:ro \
  -v $(pwd)/logs:/app/logs \
  binance-arbitrage-bot:latest \
  python main.py --live
```

## 运行模式说明

### 回测模式 (Backtest)
- **最安全**：使用历史数据测试策略
- **不需要 API 密钥**
- **推荐用于**：验证策略逻辑、参数调优

```bash
docker-compose up  # 默认就是回测模式
```

### 测试网模式 (Testnet)
- **需要测试网 API 密钥**
- **使用虚拟资金**
- **推荐用于**：验证实时连接、订单执行

编辑 `docker-compose.yml`，修改 command：
```yaml
command: ["python", "main.py", "--testnet"]
```

### 实盘模式 (Live)
- **⚠️ 使用真实资金！**
- **需要实盘 API 密钥**
- **推荐用于**：小额测试后谨慎使用

编辑 `docker-compose.yml`，修改 command：
```yaml
command: ["python", "main.py", "--live"]
```

## 常用命令

### 容器管理

```bash
# 查看运行中的容器
docker-compose ps

# 进入容器内部（调试用）
docker-compose exec binance-bot bash

# 重启容器
docker-compose restart

# 查看容器资源使用
docker stats binance-arbitrage-bot

# 清理停止的容器
docker-compose down
```

### 日志查看

```bash
# 实时查看日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100

# 查看特定时间的日志
docker-compose logs --since 2024-01-01T10:00:00
```

### 镜像管理

```bash
# 查看镜像
docker images | grep binance-arbitrage-bot

# 删除旧镜像
docker rmi binance-arbitrage-bot:latest

# 重新构建（不使用缓存）
docker-compose build --no-cache

# 清理未使用的镜像
docker image prune
```

## 配置说明

### 资源限制

在 `docker-compose.yml` 中配置资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # 最多使用 2 个 CPU 核心
      memory: 2G       # 最多使用 2GB 内存
    reservations:
      cpus: '0.5'      # 至少保证 0.5 核心
      memory: 512M     # 至少保证 512MB 内存
```

### 环境变量

创建 `.env` 文件（从 `.env.example` 复制）：

```bash
cp .env.example .env
nano .env
```

## 生产环境建议

### 1. 使用专用网络

```yaml
networks:
  bot-network:
    driver: bridge

services:
  binance-bot:
    networks:
      - bot-network
```

### 2. 添加健康检查

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import binance_rust_py; print('OK')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 3. 配置重启策略

```yaml
restart: unless-stopped  # 或 always
```

### 4. 使用 Docker Secrets（生产环境）

```bash
# 创建 secrets
echo "your_api_key" | docker secret create binance_api_key -
echo "your_api_secret" | docker secret create binance_api_secret -
```

### 5. 定期备份日志

```bash
# 定时任务备份日志
0 0 * * * tar -czf ~/backups/bot-logs-$(date +\%Y\%m\%d).tar.gz /path/to/logs/
```

## 故障排查

### 问题 1: 镜像构建失败

```bash
# 清理构建缓存后重试
docker builder prune
docker-compose build --no-cache
```

### 问题 2: 容器无法启动

```bash
# 查看详细错误信息
docker-compose logs binance-bot

# 检查配置文件
docker-compose config
```

### 问题 3: 权限问题

```bash
# 确保日志目录权限正确
chmod 755 logs/
```

### 问题 4: 连接问题

```bash
# 检查容器网络
docker network inspect bridge

# 测试网络连接
docker-compose exec binance-bot ping -c 3 api.binance.com
```

## 性能优化

### 1. 使用多阶段构建（已实现）

Dockerfile 已使用多阶段构建，最终镜像只包含运行时必需的文件。

### 2. 启用 BuildKit

```bash
export DOCKER_BUILDKIT=1
docker-compose build
```

### 3. 使用构建缓存

```bash
# 首次构建后，后续构建会更快
docker-compose build
```

## 监控和告警

### 查看实时指标

```bash
# CPU、内存使用
docker stats binance-arbitrage-bot

# 容器事件
docker events --filter container=binance-arbitrage-bot
```

### 集成 Prometheus（可选）

未来可以添加 Prometheus 和 Grafana 进行监控。

## 安全建议

1. ✅ **不要在镜像中包含 API 密钥**
2. ✅ **使用只读挂载配置文件** (`:ro`)
3. ✅ **定期更新基础镜像**
4. ✅ **使用最小权限运行**
5. ✅ **开启日志审计**

## 更新流程

```bash
# 1. 停止现有容器
docker-compose down

# 2. 拉取最新代码
git pull

# 3. 重新构建镜像
docker-compose build

# 4. 启动新容器
docker-compose up -d

# 5. 验证运行状态
docker-compose logs -f
```

## 卸载

```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi binance-arbitrage-bot:latest

# 清理卷（可选，会删除数据）
docker volume prune
```

## 总结

使用 Docker 的优势：
- ✅ 环境一致性
- ✅ 快速部署
- ✅ 资源隔离
- ✅ 易于扩展
- ✅ 简化依赖管理

推荐的使用流程：
1. 回测模式验证策略 ✅
2. 测试网模式验证连接 ⚠️
3. 小额实盘测试 ⚠️⚠️
4. 逐步增加资金 ⚠️⚠️⚠️

#!/bin/bash
# 币安套利机器人 - 快速启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}币安套利机器人 - 快速启动${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: docker-compose 未安装${NC}"
    exit 1
fi

# 检查配置文件
if [ ! -f "config/config.yaml" ]; then
    echo -e "${YELLOW}警告: 配置文件不存在，从模板复制...${NC}"
    cp config/config.example.yaml config/config.yaml
    echo -e "${YELLOW}请编辑 config/config.yaml 配置你的 API 密钥${NC}"
    echo -e "${YELLOW}回测模式不需要真实 API 密钥${NC}"
fi

# 创建必要目录
mkdir -p logs data

# 显示菜单
echo -e "${GREEN}请选择运行模式:${NC}"
echo "1) 回测模式 (Backtest) - 最安全，使用历史数据"
echo "2) 测试网模式 (Testnet) - 需要测试网 API，使用虚拟资金"
echo "3) 实盘模式 (Live) - ⚠️  使用真实资金，谨慎！"
echo "4) 构建镜像"
echo "5) 查看日志"
echo "6) 停止容器"
echo "7) 进入容器调试"
echo "0) 退出"
echo ""

read -p "请输入选项 [1-7]: " choice

case $choice in
    1)
        echo -e "${GREEN}启动回测模式...${NC}"
        docker-compose up
        ;;
    2)
        echo -e "${YELLOW}启动测试网模式...${NC}"
        # 临时修改 docker-compose.yml 的 command
        docker-compose run --rm binance-bot python main.py --testnet
        ;;
    3)
        echo -e "${RED}⚠️  警告: 即将启动实盘模式！${NC}"
        read -p "确认使用真实资金交易? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            docker-compose run --rm binance-bot python main.py --live
        else
            echo "已取消"
        fi
        ;;
    4)
        echo -e "${GREEN}构建 Docker 镜像...${NC}"
        docker-compose build
        echo -e "${GREEN}构建完成！${NC}"
        ;;
    5)
        echo -e "${GREEN}查看日志 (Ctrl+C 退出)...${NC}"
        docker-compose logs -f
        ;;
    6)
        echo -e "${YELLOW}停止容器...${NC}"
        docker-compose down
        echo -e "${GREEN}已停止${NC}"
        ;;
    7)
        echo -e "${GREEN}进入容器...${NC}"
        docker-compose exec binance-bot bash
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

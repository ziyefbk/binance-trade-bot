@echo off
REM 币安套利机器人 - Windows 快速启动脚本
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================
echo 币安套利机器人 - 快速启动
echo ================================
echo.

REM 检查 Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker 未安装或未在 PATH 中
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] docker-compose 未安装或未在 PATH 中
    pause
    exit /b 1
)

REM 检查配置文件
if not exist "config\config.yaml" (
    echo [警告] 配置文件不存在，从模板复制...
    copy config\config.example.yaml config\config.yaml
    echo [提示] 请编辑 config\config.yaml 配置你的 API 密钥
    echo [提示] 回测模式不需要真实 API 密钥
    echo.
)

REM 创建必要目录
if not exist "logs" mkdir logs
if not exist "data" mkdir data

:menu
echo.
echo 请选择运行模式:
echo 1) 回测模式 (Backtest) - 最安全，使用历史数据
echo 2) 测试网模式 (Testnet) - 需要测试网 API，使用虚拟资金
echo 3) 实盘模式 (Live) - ⚠️  使用真实资金，谨慎！
echo 4) 构建镜像
echo 5) 查看日志
echo 6) 停止容器
echo 7) 后台运行（回测模式）
echo 8) 查看容器状态
echo 0) 退出
echo.

set /p choice="请输入选项 [0-8]: "

if "%choice%"=="1" goto backtest
if "%choice%"=="2" goto testnet
if "%choice%"=="3" goto live
if "%choice%"=="4" goto build
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto stop
if "%choice%"=="7" goto background
if "%choice%"=="8" goto status
if "%choice%"=="0" goto end
echo [错误] 无效选项
goto menu

:backtest
echo [启动] 回测模式...
docker-compose up
goto end

:testnet
echo [启动] 测试网模式...
docker-compose run --rm binance-bot python main.py --testnet
goto end

:live
echo.
echo ⚠️  警告: 即将启动实盘模式！
set /p confirm="确认使用真实资金交易? (yes/no): "
if /i "%confirm%"=="yes" (
    docker-compose run --rm binance-bot python main.py --live
) else (
    echo 已取消
)
goto end

:build
echo [构建] Docker 镜像...
docker-compose build
if %errorlevel% equ 0 (
    echo [完成] 构建成功！
) else (
    echo [错误] 构建失败
)
pause
goto menu

:logs
echo [日志] 查看日志 (Ctrl+C 退出)...
docker-compose logs -f
goto menu

:stop
echo [停止] 停止容器...
docker-compose down
echo [完成] 已停止
pause
goto menu

:background
echo [启动] 后台运行回测模式...
docker-compose up -d
echo [完成] 容器已在后台运行
echo [提示] 使用选项 5 查看日志，使用选项 6 停止
pause
goto menu

:status
echo [状态] 容器运行状态:
docker-compose ps
echo.
echo [统计] 资源使用:
docker stats --no-stream binance-arbitrage-bot
pause
goto menu

:end
echo.
echo 退出程序
pause

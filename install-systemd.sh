#!/bin/bash
# install-systemd.sh — 将 Flask API 安装为系统服务（开机自启）
# 用法: sudo bash install-systemd.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🔧 安装 Flask API systemd 服务..."

# 1. 复制 service 文件
cp docs/flask-api.service /etc/systemd/system/
echo -e "${GREEN}✅${NC} 服务文件已复制到 /etc/systemd/system/"

# 2. 重载 systemd
systemctl daemon-reload
echo -e "${GREEN}✅${NC} systemd 已重载"

# 3. 先停止 run.sh 启动的实例（如果有）
if [ -f .api.pid ]; then
    pid=$(cat .api.pid)
    if ps -p "$pid" > /dev/null 2>&1; then
        kill "$pid" 2>/dev/null || true
        echo -e "${GREEN}✅${NC} 原进程 (PID: $pid) 已停止"
    fi
    rm -f .api.pid
fi

# 4. 启动并设为开机自启
systemctl enable --now flask-api
echo -e "${GREEN}✅${NC} flask-api 已启动并设为开机自启"

# 5. 验证
sleep 1
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
systemctl status flask-api --no-pager -l 2>&1 || true
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 6. 功能测试
echo ""
echo "🧪 测试接口连通性..."
if curl -s http://127.0.0.1:5000/api/health | grep -q ok; then
    echo -e "${GREEN}✅${NC} API 健康检查通过"
else
    echo -e "${RED}❌${NC} API 健康检查失败！查看日志: journalctl -u flask-api -n 20"
fi

echo ""
echo "📋 常用命令:"
echo "   systemctl status flask-api    # 查看状态"
echo "   systemctl restart flask-api   # 重启"
echo "   journalctl -u flask-api -f    # 实时日志"

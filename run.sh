#!/bin/bash
# run.sh — API 测试环境管理脚本
# 用法: ./run.sh {start|stop|restart|status|test|test-all|logs}

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$PROJECT_DIR/.api.pid"
LOG_FILE="$PROJECT_DIR/logs/api.log"
API_DIR="$PROJECT_DIR/api"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

count_instances() {
    ps aux | grep "python3 app.py" | grep -v grep | wc -l
}

start() {
    if is_running; then
        echo -e "${YELLOW}⚠️  API 已在运行 (PID: $(cat $PID_FILE))${NC}"
        return
    fi

    echo -e "${GREEN}🚀 启动 API 服务...${NC}"
    cd "$API_DIR"
    python3 app.py >> "$LOG_FILE" 2>&1 &
    local pid=$!

    echo "$pid" > "$PID_FILE"
    sleep 2

    if is_running; then
        echo -e "${GREEN}✅ API 已启动${NC}"
        echo "   PID: $pid"
        echo "   地址: http://127.0.0.1:5000"
        echo "   日志: $LOG_FILE"
    else
        echo -e "${RED}❌ 启动失败！查看日志: $LOG_FILE${NC}"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop() {
    if ! is_running; then
        echo -e "${YELLOW}⚠️  API 未运行${NC}"
        rm -f "$PID_FILE"
        return
    fi

    local pid=$(cat "$PID_FILE")
    echo -n "🛑 停止 API (PID: $pid)..."

    kill "$pid" 2>/dev/null || true

    for i in $(seq 1 10); do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            echo -e " ${GREEN}✅ 已停止${NC}"
            rm -f "$PID_FILE"
            return
        fi
        sleep 1
    done

    echo -n " 超时，强制终止..."
    kill -9 "$pid" 2>/dev/null || true
    sleep 1
    rm -f "$PID_FILE"
    echo -e " ${GREEN}✅ 已强制停止${NC}"
}

status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        local mem_mb=$(ps -p "$pid" -o rss= 2>/dev/null | awk '{printf "%.1f", $1/1024}')
        echo -e "${GREEN}✅ API 运行中${NC}"
        echo "   PID:     $pid"
        echo "   启动时间: $(ps -p $pid -o lstart= 2>/dev/null)"
        echo "   CPU:     $(ps -p $pid -o %cpu= 2>/dev/null)%"
        echo "   内存:    ${mem_mb} MB"
        echo "   并发实例: $(count_instances)"
    else
        echo -e "${RED}❌ API 未运行${NC}"
    fi
}

restart() {
    stop
    sleep 1
    start
}

test_smoke() {
    echo "🧪 运行冒烟测试..."
    cd "$PROJECT_DIR"
    python3 -m pytest tests/test_api.py -v -m smoke
}

test_all() {
    echo "🧪 运行全部测试..."
    cd "$PROJECT_DIR"
    python3 -m pytest tests/test_api.py -v --html=reports/report.html --self-contained-html
    echo "✅ 报告: reports/report.html"
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}❌ 日志文件不存在: $LOG_FILE${NC}"
    fi
}

case "${1:-help}" in
    start)    start ;;
    stop)     stop ;;
    restart)  restart ;;
    status)   status ;;
    test)     test_smoke ;;
    test-all) test_all ;;
    logs)     logs ;;
    help|*)
        echo "用法: ./run.sh {start|stop|restart|status|test|test-all|logs}"
        echo ""
        echo "  start    — 启动 API 服务（后台）"
        echo "  stop     — 停止 API 服务（优雅→强制）"
        echo "  restart  — 重启 API 服务"
        echo "  status   — 查看服务状态（PID/CPU/内存/运行时间）"
        echo "  test     — 运行冒烟测试"
        echo "  test-all — 运行全部测试 + HTML 报告"
        echo "  logs     — 实时查看日志"
        ;;
esac

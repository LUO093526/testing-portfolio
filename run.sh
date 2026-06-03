#!/bin/bash
# 一键启动测试环境

case "${1:-start}" in
  start)
    echo "🚀 启动 API 服务..."
    cd "$(dirname "$0")/api"
    python3 app.py &
    sleep 2
    echo "✅ API 已启动: http://127.0.0.1:5000"
    echo "   健康检查: http://127.0.0.1:5000/api/health"
    ;;
  test)
    echo "🧪 运行冒烟测试..."
    cd "$(dirname "$0")"
    python3 -m pytest tests/test_api.py -v -m smoke
    ;;
  test-all)
    echo "🧪 运行全部测试..."
    cd "$(dirname "$0")"
    python3 -m pytest tests/test_api.py -v --html=reports/report.html --self-contained-html
    echo "✅ 报告: reports/report.html"
    ;;
  test-crud)
    echo "🧪 运行 CRUD 测试..."
    cd "$(dirname "$0")"
    python3 -m pytest tests/test_api.py -v -m crud
    ;;
  stop)
    echo "🛑 停止 API..."
    pkill -f "python3 app.py" 2>/dev/null && echo "✅ 已停止" || echo "⚠️ 未找到运行实例"
    ;;
  *)
    echo "用法: ./run.sh {start|test|test-all|test-crud|stop}"
    ;;
esac

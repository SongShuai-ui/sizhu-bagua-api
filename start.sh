#!/bin/bash
# 四柱八卦 API 启动脚本
# 用法: bash start.sh              → 启动服务 (端口 8001)
#       bash start.sh 9000         → 指定端口
#       bash start.sh --reload     → 开发模式（热重载）

PORT=${1:-8001}
RELOAD=""

if [ "$1" = "--reload" ] || [ "$2" = "--reload" ]; then
    RELOAD="--reload"
fi

echo "🀄️  四柱八卦 API v2.1"
echo "   地址: http://localhost:${PORT}"
echo "   文档: http://localhost:${PORT}/docs"
echo ""

cd "$(dirname "$0")"
uvicorn api_server:app --host 0.0.0.0 --port "$PORT" $RELOAD

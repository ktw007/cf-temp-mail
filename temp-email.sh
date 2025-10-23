#!/bin/bash

# Cloudflare 临时邮箱管理脚本 - Shell 包装器
# 自动加载 .env 文件并执行 Python 脚本

set -e

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载环境变量
ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 错误: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并填写您的配置:"
    echo "  cp .env.example .env"
    echo "  编辑 .env 文件，填写您的 Cloudflare API 凭证"
    exit 1
fi

# 导出环境变量
set -a
source "$ENV_FILE"
set +a

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "请安装 Python 3.6 或更高版本"
    exit 1
fi

# 执行 Python 脚本
python3 "$SCRIPT_DIR/temp_email.py" "$@"

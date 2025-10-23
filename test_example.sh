#!/bin/bash
# 这是一个示例脚本，展示如何在其他脚本中使用临时邮箱生成器

set -e

echo "🧪 临时邮箱使用示例"
echo "===================="
echo ""

# 1. 创建临时邮箱
echo "1️⃣ 创建临时邮箱用于测试..."
./temp-email.sh create --prefix example --description "示例脚本测试邮箱"

echo ""

# 2. 列出所有邮箱
echo "2️⃣ 列出所有临时邮箱..."
./temp-email.sh list

echo ""
echo "✅ 示例完成！"
echo ""
echo "💡 提示:"
echo "   - 您现在可以使用创建的临时邮箱接收邮件"
echo "   - 邮件会自动转发到您的真实邮箱"
echo "   - 使用完毕后，运行 './temp-email.sh cleanup' 清理"

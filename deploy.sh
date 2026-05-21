#!/bin/bash

set -e

PROJECT_DIR="/root/student-points"

echo "开始部署..."

# 创建目录
mkdir -p $PROJECT_DIR/postgres
mkdir -p $PROJECT_DIR/backups

# 生成 SECRET_KEY
if [ ! -f .env ]; then
  SECRET_KEY=$(openssl rand -hex 32)
  echo "SECRET_KEY=$SECRET_KEY" > .env
  echo "DB_PASSWORD=Zty256310x!" >> .env
  echo "已生成 .env 文件"
fi

# 构建前端
echo "构建前端..."
cd frontend
npm install
npm run build
cd ..

# 复制前端文件
echo "复制前端文件..."
cp -r frontend/dist backend/static

# 构建并启动服务
echo "启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 验证部署
echo "验证部署..."
if curl -s http://localhost:8866/health > /dev/null; then
  echo "✓ 后端服务启动成功"
else
  echo "✗ 后端服务启动失败"
fi

if curl -s http://localhost > /dev/null; then
  echo "✓ 前端服务启动成功"
else
  echo "✗ 前端服务启动失败"
fi

echo ""
echo "部署完成！"
echo "访问地址: http://124.223.107.60"
echo "API 文档: http://124.223.107.60:8866/docs"
echo "管理后台: http://124.223.107.60/admin-panel"

#!/bin/bash
# 启动Django后端服务器

cd /var/www/harry-insurance
echo "正在启动Django后端服务器（端口8007）..."
#python3 manage.py runserver 0.0.0.0:8007
uvicorn backend.asgi:application --host 0.0.0.0 --port 8007

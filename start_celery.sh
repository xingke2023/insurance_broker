#!/bin/bash
# Celery Worker启动脚本

# 切换到项目目录
cd /var/www/harry-insurance2

# 激活虚拟环境（如果使用的话）
# source venv/bin/activate

# 启动Celery Worker
# 参数说明：
#   -A backend: 指定Celery应用位置
#   worker: 启动worker进程
#   --loglevel=info: 日志级别
#   --concurrency=4: 并发worker数量（根据服务器CPU核心数调整）
#   --max-tasks-per-child=50: 每个worker处理50个任务后重启
#   --logfile=logs/celery.log: 日志文件路径

# 创建日志目录
mkdir -p logs

# 启动Celery Worker（前台运行，用于测试）
# celery -A backend worker \
#   --loglevel=info \
#   --concurrency=4 \
#   --max-tasks-per-child=50 \
#   --logfile=logs/celery.log \
#   --pidfile=logs/celery.pid

# 后台运行版本（生产环境）
celery -A backend worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=50 \
  --logfile=logs/celery.log \
  --pidfile=logs/celery.pid \
  --detach

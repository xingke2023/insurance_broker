#!/bin/bash
# 启动所有服务的脚本

# Conda环境路径
PYTHON_EXEC="/home/ubuntu/miniconda3/envs/harry-insurance/bin/python"
CELERY_EXEC="/home/ubuntu/miniconda3/envs/harry-insurance/bin/celery"

cd /var/www/harry-insurance2

echo "================================"
echo "启动保险计划书分析系统"
echo "================================"
echo ""

# 创建日志目录
mkdir -p logs

# 1. 检查Redis
echo "1. 检查Redis服务..."
if redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis运行正常"
else
    echo "   ❌ Redis未运行，请先启动Redis"
    echo "   执行: sudo systemctl start redis"
    exit 1
fi
echo ""

# 2. 启动Django
echo "2. 启动Django服务 (端口8017)..."
if ps aux | grep -v grep | grep "manage.py runserver 0.0.0.0:8017" > /dev/null; then
    echo "   ⚠️  Django已经在运行"
else
    nohup $PYTHON_EXEC manage.py runserver 0.0.0.0:8017 > logs/django.log 2>&1 &
    sleep 3
    if ps aux | grep -v grep | grep "manage.py runserver" > /dev/null; then
        echo "   ✅ Django启动成功"
    else
        echo "   ❌ Django启动失败，请查看 logs/django.log"
        exit 1
    fi
fi
echo ""

# 3. 启动Celery Worker
echo "3. 启动Celery Worker..."
if ps aux | grep -v grep | grep "celery.*worker" > /dev/null; then
    echo "   ⚠️  Celery Worker已经在运行"
else
    nohup $CELERY_EXEC -A backend worker \
        --loglevel=info \
        --concurrency=4 \
        --max-tasks-per-child=50 \
        --logfile=logs/celery.log \
        --pidfile=logs/celery.pid > /dev/null 2>&1 &
    sleep 3
    if ps aux | grep -v grep | grep "celery.*worker" > /dev/null; then
        echo "   ✅ Celery Worker启动成功"
    else
        echo "   ❌ Celery Worker启动失败，请查看 logs/celery.log"
        exit 1
    fi
fi
echo ""

echo "================================"
echo "所有服务启动完成！"
echo "================================"
echo ""
echo "服务状态："
echo "  - Django: http://localhost:8017"
echo "  - Redis: localhost:6379"
echo "  - Celery Worker: 运行中"
echo ""
echo "日志文件："
echo "  - Django日志: logs/django.log"
echo "  - Celery日志: logs/celery.log"
echo ""
echo "查看日志: tail -f logs/django.log"
echo "停止服务: ./stop_all.sh"
echo ""

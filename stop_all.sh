#!/bin/bash
# 停止所有服务的脚本

cd /var/www/harry-insurance2

echo "================================"
echo "停止保险计划书分析系统"
echo "================================"
echo ""

# 1. 停止Django
echo "1. 停止Django服务..."
DJANGO_PIDS=$(ps aux | grep -v grep | grep "manage.py runserver" | awk '{print $2}')
if [ -n "$DJANGO_PIDS" ]; then
    for PID in $DJANGO_PIDS; do
        kill $PID 2>/dev/null
        echo "   已停止Django进程 $PID"
    done
else
    echo "   Django未运行"
fi
echo ""

# 2. 停止Celery Worker
echo "2. 停止Celery Worker..."
if [ -f "logs/celery.pid" ]; then
    PID=$(cat logs/celery.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "   已停止Celery进程 $PID"
        sleep 2
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID
            echo "   强制停止Celery进程 $PID"
        fi
        rm logs/celery.pid
    else
        rm logs/celery.pid
    fi
fi

CELERY_PIDS=$(ps aux | grep -v grep | grep "celery.*worker" | awk '{print $2}')
if [ -n "$CELERY_PIDS" ]; then
    for PID in $CELERY_PIDS; do
        kill $PID 2>/dev/null
        echo "   已停止Celery进程 $PID"
    done
else
    echo "   Celery未运行"
fi
echo ""

echo "================================"
echo "所有服务已停止"
echo "================================"
echo ""

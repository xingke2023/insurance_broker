#!/bin/bash
# Celery Worker停止脚本

echo "正在停止Celery Worker..."

# 方法1: 使用pidfile停止
if [ -f "logs/celery.pid" ]; then
    PID=$(cat logs/celery.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "已发送停止信号到进程 $PID"
        sleep 2
        # 如果还在运行，强制停止
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID
            echo "已强制停止进程 $PID"
        fi
        rm logs/celery.pid
    else
        echo "PID文件存在但进程不存在，删除PID文件"
        rm logs/celery.pid
    fi
fi

# 方法2: 查找所有celery进程并停止
CELERY_PIDS=$(ps aux | grep 'celery.*worker' | grep -v grep | awk '{print $2}')

if [ -n "$CELERY_PIDS" ]; then
    echo "找到以下Celery进程: $CELERY_PIDS"
    for PID in $CELERY_PIDS; do
        kill $PID 2>/dev/null
        echo "已停止进程 $PID"
    done
    sleep 2
    # 确认停止
    REMAINING=$(ps aux | grep 'celery.*worker' | grep -v grep)
    if [ -n "$REMAINING" ]; then
        echo "部分进程仍在运行，强制停止..."
        pkill -9 -f 'celery.*worker'
    fi
else
    echo "没有找到运行中的Celery进程"
fi

echo "✅ Celery Worker已停止"

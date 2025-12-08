# Celery异步任务系统使用说明

## 概述

本项目使用Celery + Redis实现异步任务处理，用于处理保险文档OCR结果的分析和提取。

## 系统架构

```
用户上传文档 → Django保存OCR内容 → Celery任务队列 → Worker处理任务
                                   ↓
                               Redis消息队列
                                   ↓
                          任务结果存储到Django DB
```

## 任务流水线

当用户保存OCR结果到数据库时，系统会自动启动一个三阶段的任务流水线：

1. **步骤1: 提取基本信息** (0-33%)
   - 任务: `api.tasks.extract_basic_info_task`
   - 提取受保人、保险产品、保额、保费等核心信息
   - 完成后自动触发步骤2

2. **步骤2: 提取年度价值表** (33-66%)
   - 任务: `api.tasks.extract_table_task`
   - 从OCR文本提取保单年度价值表
   - 完成后自动触发步骤3

3. **步骤3: 提取计划书概要** (66-100%)
   - 任务: `api.tasks.extract_summary_task`
   - 提取计划书整体概要、关键点、重要日期等
   - 完成后标记文档为"全部完成"

## 依赖服务

### 1. Redis (消息队列)
```bash
# 检查Redis是否运行
redis-cli ping
# 应返回: PONG

# 启动Redis (如果未运行)
sudo systemctl start redis
sudo systemctl enable redis  # 开机自启
```

### 2. Celery Worker (任务处理器)
```bash
# 方式1: 使用启动脚本 (推荐)
cd /var/www/harry-insurance2
./start_celery.sh

# 方式2: 直接命令
celery -A backend worker --loglevel=info --concurrency=4

# 后台运行
celery -A backend worker \
  --loglevel=info \
  --concurrency=4 \
  --logfile=logs/celery.log \
  --detach
```

### 3. Django服务
```bash
# 开发环境
python3 manage.py runserver

# 生产环境 (使用gunicorn等)
gunicorn backend.wsgi:application
```

## 配置说明

### Django Settings (backend/settings.py)

```python
# Celery配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis地址
CELERY_RESULT_BACKEND = 'django-db'  # 使用Django数据库存储结果
CELERY_TASK_TRACK_STARTED = True  # 跟踪任务开始状态
CELERY_TASK_TIME_LIMIT = 30 * 60  # 任务最长运行30分钟
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50  # 每个worker处理50个任务后重启
```

### Celery配置 (backend/celery.py)

Celery应用已自动配置，会自动发现`api/tasks.py`中的所有任务。

## API使用

### 1. 保存OCR结果并触发任务

**接口**: `POST /api/ocr/save/`

**请求体**:
```json
{
  "file_name": "保险计划书.pdf",
  "ocr_content": "OCR识别的文本内容...",
  "user_id": 1
}
```

**响应**:
```json
{
  "status": "success",
  "message": "保存成功",
  "document_id": 123
}
```

此时Celery任务已自动启动，开始处理文档。

### 2. 查询任务处理状态

**接口**: `GET /api/ocr/documents/{document_id}/status/`

**响应**:
```json
{
  "status": "success",
  "data": {
    "processing_stage": "extracting_basic_info",
    "progress_percentage": 20,
    "last_processed_at": "2025-01-10T12:34:56",
    "status": "processing",
    "error_message": null
  }
}
```

**处理阶段说明**:
- `pending` (0%): 等待处理
- `extracting_basic_info` (20%): 正在提取基本信息
- `basic_info_completed` (33%): 基本信息提取完成
- `extracting_table` (50%): 正在提取年度价值表
- `table_completed` (66%): 年度价值表提取完成
- `extracting_summary` (80%): 正在提取计划书概要
- `all_completed` (100%): 全部完成
- `error`: 处理出错

### 3. 前端轮询示例

```javascript
// 保存文档后，每3秒轮询一次状态
const pollStatus = async (documentId) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/ocr/documents/${documentId}/status/`);
    const data = await response.json();

    const { processing_stage, progress_percentage } = data.data;

    // 更新进度条
    updateProgressBar(progress_percentage);

    // 完成或出错时停止轮询
    if (processing_stage === 'all_completed' || processing_stage === 'error') {
      clearInterval(interval);
    }
  }, 3000);
};
```

## 监控和调试

### 查看Celery日志
```bash
tail -f logs/celery.log
```

### 查看任务执行情况
```bash
# 进入Django shell
python3 manage.py shell

# 查询任务结果
from django_celery_results.models import TaskResult
TaskResult.objects.all().order_by('-date_created')[:10]
```

### 查看Redis队列
```bash
redis-cli
> LLEN celery  # 查看队列长度
> KEYS *  # 查看所有key
```

### 清空队列 (慎用!)
```bash
redis-cli FLUSHDB
```

## 故障排查

### 问题1: Celery worker无法启动
```bash
# 检查Redis是否运行
redis-cli ping

# 检查Python依赖
pip3 list | grep celery
pip3 list | grep redis

# 查看详细错误
celery -A backend worker --loglevel=debug
```

### 问题2: 任务一直pending
```bash
# 确认worker正在运行
ps aux | grep celery

# 检查Redis连接
redis-cli ping

# 查看worker日志
tail -f logs/celery.log
```

### 问题3: 任务超时或失败
- 检查DeepSeek API密钥是否有效
- 检查网络连接
- 查看Django日志获取详细错误信息
- 任务会自动重试2次，查看重试日志

### 问题4: 数据库迁移问题
```bash
# 运行迁移
python3 manage.py migrate django_celery_results
python3 manage.py migrate api
```

## 生产环境部署

### 使用Supervisor管理Celery (推荐)

创建 `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery]
command=/home/ubuntu/bin/celery -A backend worker --loglevel=info --concurrency=4
directory=/var/www/harry-insurance2
user=ubuntu
autostart=true
autorestart=true
stdout_logfile=/var/www/harry-insurance2/logs/celery-supervisor.log
stderr_logfile=/var/www/harry-insurance2/logs/celery-supervisor-error.log
```

启动:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery
sudo supervisorctl status celery
```

### 使用Systemd管理Celery

创建 `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Service
After=network.target redis.service

[Service]
Type=forking
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/harry-insurance2
ExecStart=/home/ubuntu/bin/celery -A backend worker \
          --loglevel=info \
          --concurrency=4 \
          --logfile=/var/www/harry-insurance2/logs/celery.log \
          --pidfile=/var/www/harry-insurance2/logs/celery.pid \
          --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

启动:
```bash
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl start celery
sudo systemctl status celery
```

## 性能优化

### Worker并发数调整
根据服务器CPU核心数调整`--concurrency`参数：
- 2核: `--concurrency=2`
- 4核: `--concurrency=4`
- 8核: `--concurrency=6` (不要超过核心数太多)

### 任务超时设置
在settings.py中调整:
```python
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30分钟
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25分钟软超时
```

### Redis优化
```bash
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## 安全建议

1. **生产环境配置Redis密码**:
   ```python
   CELERY_BROKER_URL = 'redis://:password@localhost:6379/0'
   ```

2. **限制Redis访问**:
   ```bash
   # /etc/redis/redis.conf
   bind 127.0.0.1
   protected-mode yes
   ```

3. **监控任务失败率**: 设置告警机制监控任务失败

4. **日志轮转**: 配置logrotate防止日志文件过大

## 总结

- ✅ Celery + Redis提供稳定的异步任务处理
- ✅ 自动重试机制确保任务可靠执行
- ✅ 任务状态持久化到数据库，重启不丢失
- ✅ 完善的进度跟踪和错误处理
- ✅ 三阶段流水线按正确顺序执行

如有问题，请查看日志文件或联系开发团队。

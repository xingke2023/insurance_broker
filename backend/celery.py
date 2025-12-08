"""
Celery配置文件
用于处理保险文档OCR和数据提取的异步任务
"""
import os
from celery import Celery

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 创建Celery应用
app = Celery('backend')

# 使用Django配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有已注册的Django应用中的tasks.py
# 使用lambda来延迟加载settings.INSTALLED_APPS，确保Django已完全初始化
app.autodiscover_tasks(lambda: [app_config.split('.')[0] for app_config in ['api']])


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')

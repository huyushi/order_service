from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

# 创建一个Celery app
app = Celery('order_service')

#  使用CELERY_ 作为前缀，在celeryconfig.py中写配置
app.config_from_object('order_service.celery_config')

# 发现任务文件每个app下的task.py
app.autodiscover_tasks()

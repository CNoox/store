from celery import Celery
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')

celery_app = Celery('shop')

celery_app.autodiscover_tasks()

celery_app.conf.broker_url = os.environ.get('BROKER_URL')
celery_app.conf.result_backend = os.environ.get('BROKER_URL')
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.worker_concurrency = 1
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.task_acks_late = True
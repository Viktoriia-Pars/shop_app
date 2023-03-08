from __future__ import absolute_import
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTING_MODULE' , 'shop_app.settings')

app = Celery ('shop_app')

app.config_from_object('django.conf:settings' , namespace='CELERY')

app.autodiscover_tasks()
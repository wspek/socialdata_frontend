"""
 Created by waldo on 4/25/17
"""

from __future__ import absolute_import, unicode_literals
from celery import Celery
import os


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialdata_site.settings')

app = Celery('socialdata_site')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

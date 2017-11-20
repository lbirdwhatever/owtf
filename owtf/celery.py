from __future__ import absolute_import

from celery import Celery
from celery.app.task import Task

from owtf.runner.settings import settings

app = Celery('owtf-workers')
app.config_from_object(settings)

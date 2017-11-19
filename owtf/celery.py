from __future__ import absolute_import

from celery import Celery
from celery.app.task import Task

from owtf.runner.settings import settings

class Worker(Task):
    def apply_async(self, *args, **kwargs):
            return Task.apply_async(self, *args, **kwargs)


app = Celery('owtf')
app.config_from_object(settings)

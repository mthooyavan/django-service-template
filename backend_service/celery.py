from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab  # pylint: disable=unused-import
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_service.settings')

# pylint: disable=invalid-name
app = Celery('backend_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Task Routing
# https://docs.celeryproject.org/en/stable/userguide/routing.html
#
# app.conf.task_routes = {
#     'couriers.*': {'queue': 'couriers'},
#     'engineering.tasks.celery_queue_health_check': {'queue': 'engineering'},
#     'engineering.tasks.application_health_check': {'queue': 'engineering'},
# }

app.conf.tasks_acks_late = settings.CELERY_TASKS_ACK_LATE or False


# https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules
app.conf.beat_schedule = {

    ###################################################################
    # Please order the cron schedule based on frequency of it running #
    ###################################################################

    # Example
    # Executes every minute
    # 'scheduled-tasks-executor': {
    #     'task': 'engineering.tasks.scheduled_tasks_executor',
    #     'schedule': crontab(minute='*'),
    #     'args': (),
    # },
}

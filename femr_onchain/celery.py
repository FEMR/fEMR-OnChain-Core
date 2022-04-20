from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "femr_onchain.settings")
app = Celery("femr_onchain")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "reset-sessions": {
        "task": "main.background_tasks.reset_sessions",
        "schedule": crontab(),
    },
    "run-user-deactivate": {
        "task": "main.background_tasks.run_user_deactivate",
        "schedule": crontab(minute=0, hour=0),
    },
    "run-encounter-close": {
        "task": "main.background_tasks.run_encounter_close",
        "schedule": crontab(minute=0, hour=0),
    },
    "assign-broken-patients": {
        "task": "main.background_tasks.assign_broken_patient",
        "schedule": crontab(minute=0, hour=0),
    },
    "delete-old-export": {
        "task": "main.background_tasks.delete_old_export",
        "schedule": crontab(minute=0, hour=0),
    },
}

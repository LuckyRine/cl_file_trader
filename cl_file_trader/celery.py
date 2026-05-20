import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cl_file_trader.settings")
app = Celery("fileshare")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cleanup-expired-files": {
        "task": "apps.files.tasks.cleanup_expired_files",
        "schedule": crontab(hour=3, minute=0),   # daily at 3am
    },
}
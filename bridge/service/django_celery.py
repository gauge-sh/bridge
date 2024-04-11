import os

from celery import Celery

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    raise ValueError(
        "DJANGO_SETTINGS_MODULE must be set in the environment to run Celery"
    )

project_name = os.environ["DJANGO_SETTINGS_MODULE"].split(".")[0]
app = Celery(project_name)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY", force=True)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

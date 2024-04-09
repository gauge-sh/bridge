# NOTE: This file is used in both local and remote environments.
#   resolve_project_dir() is not guaranteed to work in remote environments,
#   so the project_name can be set by an environment variable.

import os

from celery import Celery

from bridge.utils.filesystem import resolve_project_dir

# Discover the correct project name
if "BRIDGE_PROJECT_NAME" in os.environ:
    # For remote environments, the project name is set by the environment
    # since our strategy of reading the current working directory may not work
    project_name = os.environ["BRIDGE_PROJECT_NAME"]
else:
    # For local environments, we can resolve the project directory by looking at cwd
    project_name = resolve_project_dir().name

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_name}.settings")

app = Celery(project_name)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

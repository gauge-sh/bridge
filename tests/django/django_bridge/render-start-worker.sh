#!/usr/bin/env bash
celery -A bridge.service.celery worker -l INFO --concurrency="${TASK_CONCURRENCY:-4}"

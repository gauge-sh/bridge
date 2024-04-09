template = """#!/usr/bin/env bash
celery -A bridge.service.celery worker -l INFO --concurrency="${{TASK_CONCURRENCY:-4}}"
"""


def start_worker_sh_template() -> str:
    return template.format()

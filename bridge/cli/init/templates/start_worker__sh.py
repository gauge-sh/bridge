from bridge.framework.base import Framework

template = """#!/usr/bin/env bash
celery -A bridge.service.django_celery worker -l INFO --concurrency="${{TASK_CONCURRENCY:-4}}"
"""


def start_worker_sh_template(framework: Framework) -> str:
    if framework != Framework.DJANGO:
        raise NotImplementedError(
            f"Unsupported framework for Render platform: {framework}"
        )
    return template.format()

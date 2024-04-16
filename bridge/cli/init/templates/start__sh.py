uvicorn_worker_string = "-k uvicorn.workers.UvicornWorker"

template = """#!/usr/bin/env bash
gunicorn {app_path} -w "${{WEB_CONCURRENCY:-4}}" -b 0.0.0.0:"$PORT" {worker_string}
"""


def start_sh_template(app_path: str, is_asgi: bool = False) -> str:
    return template.format(
        app_path=app_path, worker_string=uvicorn_worker_string if is_asgi else ""
    )

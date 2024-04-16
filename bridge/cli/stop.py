import os
import signal

import docker
import psutil

from bridge.console import log_task
from bridge.utils.filesystem import resolve_dot_bridge


def stop():
    with log_task("Stopping bridge services...", "All bridge services stopped"):
        bridge_path = resolve_dot_bridge()
        # Docker - postgres, redis
        cid_path = bridge_path / "cid"
        if os.path.exists(cid_path):
            docker_client = docker.from_env()
            with open(cid_path) as f:
                for cid in f.readlines():
                    cid = cid.strip()
                    try:
                        container = docker_client.containers.get(cid)
                        container.stop()
                    except docker.errors.NotFound:
                        pass
            os.remove(cid_path)
        # Processes - celery, flower
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                # Check if the name fragment is in the command line; this field is a list
                proc_name = proc.info["cmdline"]
                if proc_name and "bridge.service.django_celery" in proc_name:
                    proc.send_signal(signal.SIGTERM)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

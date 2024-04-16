import os
import signal

import docker
import psutil

from bridge.console import log_task
from bridge.utils.filesystem import resolve_dot_bridge


def stop():
    with log_task("Stopping bridge services...", "All bridge services stopped"):
        bridge_path = resolve_dot_bridge()
        cid_path = bridge_path / "cid"

        if os.path.exists(cid_path):
            docker_client = docker.from_env()
            with open(cid_path) as f:
                for cid in f.readlines():
                    print(cid)
                    cid = cid.strip()
                    try:
                        container = docker_client.containers.get(cid)
                        container.stop()
                    except docker.errors.NotFound:
                        pass
            os.remove(cid_path)

        # pid_path = bridge_path / "pid"
        # if os.path.exists(pid_path):
        #     with open(pid_path) as f:
        #         for pid in f.readlines():
        #             pid = int(pid.strip())
        #             try:
        #                 os.kill(pid, signal.SIGTERM)
        #                 for _ in range(30):
        #                     sleep(0.1)
        #                     try:
        #                         # If this doesn't raise an error, process is still running
        #                         os.kill(pid, 0)
        #                     except OSError:
        #                         # Error raised, process is killed
        #                         continue
        #                 os.kill(pid, signal.SIGKILL)
        #             except ProcessLookupError:
        #                 pass
        #
        #     os.remove(pid_path)
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                # Check if the name fragment is in the command line; this field is a list
                proc_name = proc.info["cmdline"]
                if proc_name and "bridge.service.django_celery" in proc_name:
                    proc.send_signal(signal.SIGTERM)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

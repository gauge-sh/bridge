import os
import signal
import socket
import subprocess
import sys
from time import sleep
from typing import Any

import psutil
from rich.console import Console

from bridge.config import get_config
from bridge.console import log_info, log_task, log_warning
from bridge.framework.base import Framework, FrameWorkHandler
from bridge.platform import Platform
from bridge.platform.postgres import build_postgres_environment
from bridge.platform.redis import build_redis_environment
from bridge.utils.filesystem import resolve_dot_bridge


class DjangoHandler(FrameWorkHandler):
    FRAMEWORK = Framework.DJANGO

    def is_remote(self) -> bool:
        # Django's DEBUG mode should be disabled in production,
        # so we use it to differentiate between running locally
        # and running on an unknown remote platform.
        is_debug_mode = bool(self.framework_locals.get("DEBUG"))
        return super().is_remote() or not is_debug_mode

    def configure_services(self, platform: Platform) -> None:
        super().configure_services(platform)
        # Additional Django-specific configuration
        self.configure_staticfiles(platform)
        self.configure_allowed_hosts(platform)
        self.configure_debug(platform)
        self.configure_secret_key(platform)

    def configure_postgres(self, platform: Platform) -> None:
        if "DATABASES" in self.framework_locals:
            log_info(
                "Overwriting existing DATABASES configuration with Postgres configuration."
            )

        environment = build_postgres_environment(platform=platform)
        self.framework_locals["DATABASES"] = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": environment.db,
                "USER": environment.user,
                "PASSWORD": environment.password,
                "HOST": environment.host,
                "PORT": environment.port,
            }
        }

    def configure_allowed_hosts(self, platform: Platform) -> None:
        if platform == Platform.RENDER:
            if (
                "ALLOWED_HOSTS" in self.framework_locals
                and self.framework_locals["ALLOWED_HOSTS"]
            ):
                log_info(
                    "Overwriting ALLOWED_HOSTS configuration with Render configuration."
                )
            self.framework_locals["ALLOWED_HOSTS"] = [".onrender.com", "localhost"]

    def configure_debug(self, platform: Platform) -> None:
        if platform != Platform.LOCAL:
            if "DEBUG" in self.framework_locals and self.framework_locals["DEBUG"]:
                log_warning(
                    "DEBUG is truthy in remote environment; overwriting configuration to False."
                )
            self.framework_locals["DEBUG"] = False

    def configure_secret_key(self, platform: Platform) -> None:
        if platform != Platform.LOCAL:
            if (
                "SECRET_KEY" in self.framework_locals
                and "SECRET_KEY" in os.environ
                and self.framework_locals["SECRET_KEY"]
                and self.framework_locals != os.environ.get("SECRET_KEY")
            ):
                # If the SECRET_KEY from the current remote environment is different
                # from an explicitly set SECRET_KEY in the framework locals, we should
                # log this to the console.
                log_info("Overwriting SECRET_KEY configuration in remote environment.")
            self.framework_locals["SECRET_KEY"] = os.environ.get(
                "SECRET_KEY", self.framework_locals.get("SECRET_KEY", "")
            )

    def configure_staticfiles(self, platform: Platform):
        if platform == Platform.RENDER:
            if (
                "STATIC_URL" in self.framework_locals
                or "STATIC_ROOT" in self.framework_locals
                or "STATICFILES_DIRS" in self.framework_locals
                or "STATICFILES_STORAGE" in self.framework_locals
            ):
                log_info(
                    "Overwriting existing staticfiles configuration with Render configuration."
                )
            self.framework_locals["STATIC_URL"] = "/static/"
            self.framework_locals["STATIC_ROOT"] = os.path.join(
                self.framework_locals["BASE_DIR"], "staticfiles"
            )
            self.framework_locals["STATICFILES_STORAGE"] = (
                "whitenoise.storage.CompressedManifestStaticFilesStorage"
            )
            middleware: list[str] = self.framework_locals.get("MIDDLEWARE", [])
            if "whitenoise.middleware.WhiteNoiseMiddleware" not in middleware:
                security_middleware_idx = next(
                    (
                        i
                        for i, middleware in enumerate(middleware)
                        if middleware == "django.middleware.security.SecurityMiddleware"
                    ),
                    None,
                )
                if security_middleware_idx is not None:
                    middleware.insert(  # TODO this won't work with a tuple, we may want to modify
                        security_middleware_idx + 1,
                        "whitenoise.middleware.WhiteNoiseMiddleware",
                    )
                else:
                    middleware.insert(0, "whitenoise.middleware.WhiteNoiseMiddleware")
            self.framework_locals["MIDDLEWARE"] = middleware

    def configure_worker(self, platform: Platform) -> None:
        environment = build_redis_environment(platform)
        self.framework_locals["CELERY_BROKER_URL"] = environment.url
        self.framework_locals["CELERY_RESULT_BACKEND"] = environment.url

        # This will make sure the app is always imported when
        # Django starts so that shared_task will use this app.
        from bridge.service.django_celery import app  # noqa: F401 type: ignore

    def start_local_worker(self) -> None:
        # Confirm we are in a command which expects Celery to be available
        expected_command_args = {"runserver", "runserver_plus", "shell", "shell_plus"}
        if set(sys.argv) & expected_command_args:
            console = Console()
            console.print(
                "[bold bright_green]Setting up service "
                "[white]bridge_celery[/white]..."
            )
            with log_task("Starting local worker", "Local worker started"):
                from bridge.service.django_celery import app

                # Kill any active celery processes
                for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                    try:
                        proc_name = proc.info["cmdline"]
                        if (
                            proc_name
                            and "bridge.service.django_celery" in proc_name
                            and "worker" in proc_name
                        ):
                            proc.send_signal(signal.SIGTERM)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                subprocess.Popen(
                    "nohup "
                    "celery -A bridge.service.django_celery worker -c 1 -l INFO"
                    " > /dev/null 2>&1 &",
                    shell=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                while not app.control.inspect().ping():
                    # Wait for celery to start
                    sleep(0.1)
            console.print(
                "[bold bright_green]Service [white]bridge_celery[/white] started!"
            )

    def start_local_flower(self) -> None:
        # Confirm we are in a command which expects flower to be available
        expected_command_args = {"runserver", "runserver_plus", "shell", "shell_plus"}
        if set(sys.argv) & expected_command_args:
            console = Console()
            console.print(
                "[bold bright_green]Setting up service "
                "[white]bridge_flower[/white]..."
            )
            with log_task("Starting flower", "Flower started"):
                # Kill any active flower process
                for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                    try:
                        proc_name = proc.info["cmdline"]
                        if (
                            proc_name
                            and "bridge.service.django_celery" in proc_name
                            and "flower" in proc_name
                        ):
                            proc.send_signal(signal.SIGTERM)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                dot_bridge_path = resolve_dot_bridge() / "flower_db"
                subprocess.Popen(
                    "nohup "
                    "celery -A bridge.service.django_celery flower "
                    f"--persistent=True --db='{dot_bridge_path}'"
                    " > /dev/null 2>&1 &",
                    shell=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                port_bound = False
                while not port_bound:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        port_bound = s.connect_ex(("localhost", 5555)) == 0
                    sleep(0.1)

            console.print(
                "[bold bright_green]Service [white]bridge_flower[/white] started!"
            )


def configure(settings_locals: dict[Any, Any]) -> None:
    project_name = os.path.basename(settings_locals["BASE_DIR"])
    handler = DjangoHandler(
        project_name=project_name,
        framework_locals=settings_locals,
        bridge_config=get_config(),
    )
    handler.run()

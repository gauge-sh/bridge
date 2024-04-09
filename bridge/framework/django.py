import os
import subprocess
import sys

from bridge.console import log_task, log_warning
from bridge.framework.base import FrameWorkHandler
from bridge.platform import Platform
from bridge.platform.postgres import build_postgres_environment
from bridge.platform.redis import build_redis_environment


class DjangoHandler(FrameWorkHandler):
    def is_remote(self) -> bool:
        # Django's DEBUG mode should be disabled in production,
        # so we use it to differentiate between running locally
        # and running on an unknown remote platform.
        is_debug_mode = bool(self.framework_locals.get("DEBUG"))
        return super().is_remote() or not is_debug_mode

    def configure_postgres(self, platform: Platform) -> None:
        if "DATABASES" in self.framework_locals:
            log_warning(
                "databases already configured; overwriting key. "
                "Make sure no other instances of postgres are running."
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

    def configure_staticfiles(self, platform: Platform):
        if platform == Platform.RENDER:
            if (
                "STATIC_URL" in self.framework_locals
                or "STATIC_ROOT" in self.framework_locals
                or "STATICFILES_DIRS" in self.framework_locals
                or "STATICFILES_STORAGE" in self.framework_locals
            ):
                log_warning(
                    "staticfiles already configured; overwriting configuration."
                )
                self.framework_locals["STATIC_URL"] = "/static/"
                self.framework_locals["STATIC_ROOT"] = os.path.join(
                    self.framework_locals["BASE_DIR"], "staticfiles"
                )
                self.framework_locals["STATICFILES_STORAGE"] = (
                    "whitenoise.storage.CompressedManifestStaticFilesStorage"
                )

    def configure_worker(self, platform: Platform) -> None:
        environment = build_redis_environment(platform)
        self.framework_locals["CELERY_BROKER_URL"] = environment.url
        self.framework_locals["CELERY_RESULT_BACKEND"] = environment.url

    def start_local_worker(self) -> None:
        # Confirm we are in a `runserver` command
        if sys.argv[1] == "runserver":
            # This will make sure the app is always imported when
            # Django starts so that shared_task will use this app.
            from bridge.service.celery import app  # noqa: F401

            with log_task("Starting local worker", "Local worker started"):
                try:
                    subprocess.run(
                        ["celery", "-A", "bridge.service.celery", "status"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )

                except subprocess.SubprocessError:
                    subprocess.Popen(
                        [
                            "celery",
                            "-A",
                            "bridge.service.celery",
                            "worker",
                            "-l",
                            "INFO",
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )


def configure(
    settings_locals: dict,
    enable_postgres: bool = True,
    enable_worker: bool = True,
) -> None:
    project_name = os.path.basename(settings_locals["BASE_DIR"])
    handler = DjangoHandler(
        project_name=project_name,
        framework_locals=settings_locals,
        enable_postgres=enable_postgres,
        enable_worker=enable_worker,
    )
    handler.run()

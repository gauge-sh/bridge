import os

from bridge.console import log_warning
from bridge.framework.base import FrameWorkHandler
from bridge.platform import Platform
from bridge.platform.postgres import build_postgres_environment


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

    def configure_staticfiles(self):
        # TODO: set up STATIC_URL, STATIC_ROOT etc. for whitenoise setup on Render
        ...


def configure(settings_locals: dict, enable_postgres=True) -> None:
    project_name = os.path.basename(settings_locals["BASE_DIR"])

    handler = DjangoHandler(
        project_name=project_name,
        framework_locals=settings_locals,
        enable_postgres=enable_postgres,
    )
    handler.run()

import os.path

from bridge.console import log_warning
from bridge.framework.base import FrameWorkHandler
from bridge.service.postgres import PostgresEnvironment


class DjangoHandler(FrameWorkHandler):
    def configure_postgres(self, environment: PostgresEnvironment) -> None:
        if "DATABASES" in self.framework_locals:
            log_warning(
                "databases already configured; overwriting key. "
                "Make sure no other instances of postgres are running."
            )
        self.framework_locals["DATABASES"] = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": environment.POSTGRES_DB,
                "USER": environment.POSTGRES_USER,
                "PASSWORD": environment.POSTGRES_PASSWORD,
                "HOST": environment.POSTGRES_HOST,
                "PORT": environment.POSTGRES_PORT,
            }
        }


def configure(settings_locals: dict, enable_postgres=True) -> None:
    project_name = os.path.basename(settings_locals["BASE_DIR"])

    handler = DjangoHandler(
        project_name=project_name,
        framework_locals=settings_locals,
        enable_postgres=enable_postgres,
    )
    handler.run()

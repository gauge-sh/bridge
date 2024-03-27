from bridge.service.postgres import PostgresConfig
from bridge.framework.base import FrameWorkHandler


class DjangoHandler(FrameWorkHandler):
    def configure_postgres(self, config: PostgresConfig) -> None:
        if "DATABASES" in self.framework_locals:
            raise Exception(
                "databases already configured; please remove to avoid collision or turn off postgres"
            )
        self.framework_locals["DATABASES"] = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config.environment.POSTGRES_DB,
                "USER": config.environment.POSTGRES_USER,
                "PASSWORD": config.environment.POSTGRES_PASSWORD,
                "HOST": config.environment.POSTGRES_HOST,
                "PORT": config.environment.POSTGRES_PORT,
            }
        }


def configure(settings_locals: dict, enable_postgres=True) -> None:
    handler = DjangoHandler(settings_locals, enable_postgres=enable_postgres)
    handler.run()

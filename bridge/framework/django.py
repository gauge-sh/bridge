from bridge.service.postgres import PostgresService, PostgresConfig
from bridge.service.docker import get_docker_client


def configure(settings_locals: dict, postgres=True) -> None:
    client = get_docker_client()
    if postgres:
        configure_postgres(client, settings_locals)


def configure_postgres(client, settings_locals: dict) -> None:
    # todo next 3 lines could be abstracted
    config = PostgresConfig()
    service = PostgresService(client=client, config=config)
    service.start()
    if "DATABASES" in settings_locals:
        raise Exception(
            "databases already configured; please remove to avoid collision or turn off postgres"
        )
    settings_locals["DATABASES"] = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config.environment.POSTGRES_DB,
            "USER": config.environment.POSTGRES_USER,
            "PASSWORD": config.environment.POSTGRES_PASSWORD,
            "HOST": config.environment.POSTGRES_HOST,
            "PORT": config.environment.POSTGRES_PORT,
        }
    }

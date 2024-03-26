import service.docker
from bridge.service.docker import get_config


def configure(settings_locals: dict, postgres=True) -> None:
    if postgres and "DATABASES" in settings_locals:
        raise
    config = service.docker.get_config(postgres=postgres)
    if postgres:
        settings_locals["DATABASES"] = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config["postgres"]["name"],
                "USER": config["postgres"]["user"],
                "PASSWORD": config["postgres"]["password"],
                "HOST": "db",  # set in docker-compose.yml - should this be parameterized?
                "PORT": 5432,  # default postgres port - should this be unique?
            }
        }

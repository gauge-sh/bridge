from bridge.service import docker


def configure(settings_locals: dict, postgres=True) -> None:
    if postgres and "DATABASES" in settings_locals:
        raise
    config = docker.get_config(has_postgres=postgres)
    if postgres:
        settings_locals["DATABASES"] = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config["postgres"]["NAME"],
                "USER": config["postgres"]["USER"],
                "PASSWORD": config["postgres"]["PASSWORD"],
                "HOST": config["postgres"]["HOST"],
                "PORT": config["postgres"]["PORT"],
            }
        }

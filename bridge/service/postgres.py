# Responsible for postgres
import docker


def get_config(client: docker.DockerClient):
    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "db",  # set in docker-compose.yml
            "PORT": 5432,  # default postgres port
        }
    }

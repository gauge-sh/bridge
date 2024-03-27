# Responsible for postgres
from time import sleep

import docker


def pull_image(client: docker.DockerClient):
    if not client.images.list(name="postgres:12"):
        print("Postgres image not found, pulling...")
        client.images.pull("postgres:12")
        print("Postgres image pulled!")


def start_container(client: docker.DockerClient):
    env_vars = {
        "POSTGRES_USER": "postgres",  # todo parameterize
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_DB": "postgres",
    }
    containers = client.containers.list(filters={"name": "bridge_postgres"}, all=True)
    if containers:
        # Container names are unique
        [container] = containers
        if container.status in ["restarting", "paused", "exited"]:
            print("Container in bad state, restarting")
            container.restart()
            print("Container restarted")
        else:
            print("Container found!")
    else:
        # Create and start the container
        print("Creating container")
        client.containers.run(
            "postgres:12",  # Image name
            environment=env_vars,
            ports={
                "5432/tcp": 5432
            },  # Map PostgreSQL port 5432 inside the container to port 5432 on the host
            detach=True,
            name="bridge_postgres",
            # remove=True, this would remove the container once it stops running
            # restart_policy=... could have the container continually restart and make itself available
            volumes={},
        )
    sleep(3)


def get_config(client: docker.DockerClient):
    pull_image(client)
    start_container(client)
    return {
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": 5432,
    }

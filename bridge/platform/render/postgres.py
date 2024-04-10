import os

import dj_database_url

from bridge.platform.postgres import PostgresEnvironment


def build_render_postgres_environment() -> PostgresEnvironment:
    try:
        database_url = os.environ["DATABASE_URL"]
    except KeyError as e:
        raise ValueError("DATABASE_URL is required for Render Postgres") from e
    config: dj_database_url.DBConfig = dj_database_url.config(
        default=database_url,
    )
    # Assertion here satisfies pyright
    assert (
        "HOST" in config
        and "PORT" in config
        and "NAME" in config
        and "USER" in config
        and "PASSWORD" in config
    ), "DATABASE_URL configuration is missing required keys"

    port = 5432 if not config["PORT"] else int(config["PORT"])
    return PostgresEnvironment(  # key presence checked above
        host=config["HOST"],
        port=port,
        db=config["NAME"],
        user=config["USER"],
        password=config["PASSWORD"],
    )

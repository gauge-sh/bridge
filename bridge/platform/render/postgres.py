import os

import dj_database_url

from bridge.platform.postgres import PostgresEnvironment


def build_render_postgres_environment() -> PostgresEnvironment:
    try:
        database_url = os.environ["DATABASE_URL"]
    except KeyError as e:
        raise ValueError("DATABASE_URL is required for Render Postgres") from e
    config = dj_database_url.config(
        default=database_url,
    )
    if not all([key in config for key in ["HOST", "PORT", "NAME", "USER", "PASSWORD"]]):
        raise ValueError("Missing or incorrect DATABASE_URL configuration")
    return PostgresEnvironment(  # key presence checked above
        host=config["HOST"],  # type: ignore
        port=config["PORT"],  # type: ignore
        db=config["NAME"],  # type: ignore
        user=config["USER"],  # type: ignore
        password=config["PASSWORD"],  # type: ignore
    )

import os

from pydantic import BaseModel

from bridge.console import log_warning
from bridge.platform.base import Platform


class PostgresEnvironment(BaseModel):
    user: str = "postgres"
    password: str = "postgres"
    db: str = "postgres"
    host: str = "localhost"
    port: int = 5432

    @classmethod
    def from_env(cls):
        try:
            port = int(os.environ.get("POSTGRES_PORT", 5432))
        except ValueError:
            log_warning("Invalid POSTGRES_PORT; using default value.")
            port = 5432
        return cls(
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
            db=os.environ.get("POSTGRES_DB", "postgres"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=port,
        )


def build_postgres_environment(platform: Platform) -> PostgresEnvironment:
    if platform == Platform.LOCAL:
        # This uses hardcoded default values,
        # and must match the values used in the PostgresService class
        # which runs locally.
        return PostgresEnvironment()
    elif platform == Platform.RENDER:
        from bridge.platform.render import build_render_postgres_environment

        return build_render_postgres_environment()
    elif platform == Platform.UNKNOWN_REMOTE:
        # This will pull from environment variables like POSTGRES_USER, etc.
        return PostgresEnvironment.from_env()
    else:
        raise ValueError(f"Unsupported platform for configuring Postgres: {platform}")

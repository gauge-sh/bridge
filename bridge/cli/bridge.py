import argparse

from bridge.cli.db import open_database_shell
from bridge.cli.init import initialize
from bridge.cli.redis import open_redis_shell
from bridge.cli.stop import stop
from bridge.config import get_config
from bridge.framework import Framework


def detect_framework() -> Framework:
    # TODO: auto-detect framework (assuming Django)
    return Framework.DJANGO


def main():
    # Create the top-level parser for the 'bridge' command
    parser = argparse.ArgumentParser(prog="bridge")
    # TODO: tie this version output to the version in pyproject.toml
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    # Parser for 'stop'
    subparsers.add_parser("stop", help="Stop all running local services")

    # Parser for 'init' command
    init_parser = subparsers.add_parser(
        "init", help="Initialize configuration for a given platform (Render, Heroku)"
    )
    init_parser.add_argument(
        "init_platform",
        help="Platform where you want to deploy this app",
        choices=["render", "railway", "heroku"],
    )

    # Parser for db
    db_parser = subparsers.add_parser("db", help="Interact with the database")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("shell", help="Open a database shell (psql)")

    # Parser for redis
    redis_parser = subparsers.add_parser("redis", help="Interact with Redis")
    redis_subparsers = redis_parser.add_subparsers(dest="redis_command")
    redis_subparsers.add_parser("shell", help="Open a Redis shell (redis-cli)")

    # Parse the arguments
    args = parser.parse_args()
    framework = detect_framework()
    bridge_config = get_config()

    if args.command == "stop":
        stop()
    elif args.command == "init":
        initialize(
            framework=framework,
            platform=args.init_platform,
            bridge_config=bridge_config,
        )
    elif args.command == "db":
        if args.db_command == "shell":
            open_database_shell()
        else:
            db_parser.print_help()
    elif args.command == "redis":
        if args.redis_command == "shell":
            open_redis_shell()
        else:
            redis_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

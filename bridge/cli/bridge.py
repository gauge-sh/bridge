import argparse

from bridge.cli.db import open_database_shell
from bridge.cli.init import initialize
from bridge.cli.redis import open_redis_shell
from bridge.framework import Framework


def detect_framework() -> Framework:
    # TODO: auto-detect framework (assuming Django)
    return Framework.DJANGO


def main():
    # Create the top-level parser for the 'bridge' command
    parser = argparse.ArgumentParser(prog="bridge")
    # TODO: tie this version output to the version in pyproject.toml
    parser.add_argument("--version", action="version", version="%(prog)s 0.0.22")
    subparsers = parser.add_subparsers(dest="command")

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
    subparsers.add_parser("db", help="Open a database shell")

    # Parser for redis
    subparsers.add_parser("redis", help="Open a redis shell")

    # Parse the arguments
    args = parser.parse_args()
    framework = detect_framework()

    # TODO: pattern for additional config from the CLI
    if args.command == "init":
        initialize(framework=framework, platform=args.init_platform)
    elif args.command == "db":
        open_database_shell()
    elif args.command == "redis":
        open_redis_shell()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

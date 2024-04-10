import argparse

from bridge.cli.init import initialize_platform


def main():
    # Create the top-level parser for the 'bridge' command
    parser = argparse.ArgumentParser(prog="bridge")
    # TODO: tie this version output to the version in pyproject.toml
    parser.add_argument("--version", action="version", version="%(prog)s 0.0.22")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Parser for 'init' command
    init_parser = subparsers.add_parser(
        "init", help="Initialize configuration for a given platform (Render, Heroku)"
    )
    init_parser.add_argument(
        "init_platform",
        help="Platform where you want to deploy this app",
        choices=["render", "railway", "heroku"],
    )
    init_parser.add_argument(
        "--wsgi-path",
        help="Path to your WSGI application callable (ex: myapp.wsgi:application)",
        required=False,
    )
    init_parser.add_argument(
        "--asgi-path",
        help="Path to your ASGI application callable (ex: myapp.asgi:application)",
        required=False,
    )

    # Parse the arguments
    args = parser.parse_args()

    if args.command == "init":
        # Additional validation for the arguments
        if args.command == "init" and args.wsgi_path and args.asgi_path:
            parser.error("Both WSGI and ASGI paths cannot be provided")
        initialize_platform(args.init_platform)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

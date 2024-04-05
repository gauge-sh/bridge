import argparse

from .init import initialize_platform


def main():
    # Create the top-level parser for the 'bridge' command
    parser = argparse.ArgumentParser(prog="bridge")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Parser for 'init' command
    init_parser = subparsers.add_parser(
        "init", help="Initialize configuration for a given platform (Render, Heroku)"
    )
    init_parser.add_argument(
        "init_platform",
        help="Platform where you want to deploy this app",
        choices=["render", "heroku"],
    )

    # Parse the arguments
    args = parser.parse_args()

    if args.command == "init":
        initialize_platform(args.init_platform)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

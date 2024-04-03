import argparse

from bridge.cli.deploy.django import DjangoDeployer


def main():
    # Create the top-level parser for the 'bridge-sdk' command
    parser = argparse.ArgumentParser(prog="bridge-sdk")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Parser for 'deploy' command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy help")
    deploy_parser.add_subparsers(dest="deploy_command", help="Deploy sub-command help")

    # # Sub-parser for 'deploy' without sub-commands but with optional args
    # deploy_parser.add_argument(
    #     "optional_args", nargs="*", help="Optional arguments for deploy",
    #     required=False
    # )
    #
    # # Sub-parser for 'deploy list'
    # deploy_list_parser = deploy_subparsers.add_parser("list", help="List deployments")
    #
    # # Sub-parser for 'deploy rollback'
    # deploy_rollback_parser = deploy_subparsers.add_parser(
    #     "rollback", help="Rollback deployment"
    # )
    # deploy_rollback_parser.add_argument("deployment", help="Deployment to rollback")
    #
    # # Parser for 'env' command
    # env_parser = subparsers.add_parser("env", help="Environment variables management")
    # env_subparsers = env_parser.add_subparsers(
    #     dest="env_command", help="Env sub-command help"
    # )
    #
    # # Sub-parsers for 'env' sub-commands
    # env_add_parser = env_subparsers.add_parser(
    #     "add", help="Add an environment variable"
    # )
    # env_add_parser.add_argument("key", help="Key of the environment variable to add")
    #
    # env_remove_parser = env_subparsers.add_parser(
    #     "remove", help="Remove an environment variable"
    # )
    # env_remove_parser.add_argument(
    #     "key", help="Key of the environment variable to remove"
    # )
    #
    # env_list_parser = env_subparsers.add_parser(
    #     "list", help="List environment variables"
    # )

    # Parser for 'shell' command
    subparsers.add_parser("shell", help="Open a shell")

    # Parser for 'logs' command
    subparsers.add_parser("logs", help="Show logs")

    # Parse the arguments
    args = parser.parse_args()

    if args.command == "deploy":
        if args.deploy_command is None:
            # assume django for now
            DjangoDeployer(bucket_name="never-over-bridge-test").deploy()
        elif args.deploy_command == "list":
            print("Listing deployments...")
        elif args.deploy_command == "rollback":
            print(f"Rolling back deployment: {args.deployment}")

    elif args.command == "env":
        if args.env_command == "add":
            print(f"Adding environment variable: {args.key}")
        elif args.env_command == "remove":
            print(f"Removing environment variable: {args.key}")
        elif args.env_command == "list":
            print("Listing environment variables...")

    elif args.command == "shell":
        print("Opening shell...")

    elif args.command == "logs":
        print("Showing logs...")


if __name__ == "__main__":
    main()

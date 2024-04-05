# This package is responsible for implementing
# the 'init' command of the bridge CLI.
# Each platform which is supported by bridge
# will have its own implementation available


def initialize_platform(platform: str):
    print(f"Initializing configuration for {platform}...")

import os
from enum import Enum


class Platform(Enum):
    """Enumeration of supported platforms."""

    LOCAL = "local"
    UNKNOWN_REMOTE = "unknown_remote"
    HEROKU = "heroku"
    RENDER = "render"
    RAILWAY = "railway"


def detect_platform():
    """
    Detect the platform based on environment variables.

    NOTE: Assumes that the application is running in some kind of remote environment,
    since each framework may define a local/debug environment differently
    and should be checked individually, before calling this method to disambiguate.
    """
    platform = os.environ.get("BRIDGE_PLATFORM")
    if platform:
        try:
            return Platform(platform)
        except ValueError:
            return Platform.UNKNOWN_REMOTE
    return Platform.UNKNOWN_REMOTE

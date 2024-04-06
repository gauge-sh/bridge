from bridge.console import log_task
from .render import initialize_render_platform


def initialize_platform(platform: str):
    if platform == "render":
        with log_task(
            "Initializing configuration for render...",
            "Configuration initialized for render",
        ):
            initialize_render_platform()
    else:
        raise ValueError(f"Unsupported platform: {platform}")

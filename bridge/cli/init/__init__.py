from bridge.cli.init.render import build_render_init_config, initialize_render_platform
from bridge.console import log_task


def initialize_platform(platform: str):
    if platform == "render":
        # Build config outside of log_task to avoid TUI interaction with status spinner
        config = build_render_init_config()
        with log_task(
            "Initializing configuration for render...",
            "Configuration initialized for render",
        ):
            initialize_render_platform(config=config)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

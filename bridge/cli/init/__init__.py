from bridge.cli.errors import ActionCancelledError
from bridge.cli.init.render import build_render_init_config, initialize_render_platform
from bridge.console import log_info, log_task


def initialize_platform(platform: str):
    if platform == "render":
        # Build config outside of log_task to avoid TUI interaction with status spinner
        try:
            config = build_render_init_config()
        except ActionCancelledError as e:
            log_info(str(e))
            return
        with log_task(
            "Initializing configuration for render...",
            "Configuration initialized for render",
        ):
            initialize_render_platform(config=config)
    elif platform in ["railway", "heroku"]:
        log_info(f"Platform '{platform}' is not supported yet")
    else:
        raise ValueError(
            "Unknown platform provided."
            " Known platforms: ['render', 'railway', 'heroku']"
        )

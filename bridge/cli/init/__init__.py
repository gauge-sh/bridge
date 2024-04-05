from .render import initialize_render_platform


def initialize_platform(platform: str):
    if platform == "render":
        initialize_render_platform()
    else:
        raise ValueError(f"Unsupported platform: {platform}")

from .templates import build_sh_template, render_yaml_template


def initialize_render_platform():
    print("Initializing configuration for render...")
    with open(".bridge/build.sh", "w") as f:
        print("Writing build.sh")
        f.write(build_sh_template("world"))
    with open(".bridge/render.yaml", "w") as f:
        print("Writing render.yaml")
        f.write(render_yaml_template())
    print("Configuration initialized for render")

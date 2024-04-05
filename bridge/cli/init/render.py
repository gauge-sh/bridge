from .templates import build_sh_template, render_yaml_template, start_sh_template


def initialize_render_platform():
    print("Initializing configuration for render...")
    with open(".bridge/build.sh", "w") as f:
        print("Writing build.sh")
        f.write(build_sh_template())
    with open(".bridge/start.sh", "w") as f:
        # TODO: detect this somehow, handle config
        app_path = "app:app"
        print("Writing start.sh")
        f.write(start_sh_template(app_path=app_path))
    with open(".bridge/render.yaml", "w") as f:
        print("Writing render.yaml")
        f.write(
            render_yaml_template(
                service_name="bridge-deployed-service",
                repo_url="TODO: add repo url, check if required",
                database_name="bridge-deployed-db",
                database_user="bridge-user",
            )
        )
    print("Configuration initialized for render")

from .templates import build_sh_template, render_yaml_template, start_sh_template


def initialize_render_platform():
    with open(".bridge/build.sh", "w") as f:
        f.write(build_sh_template())

    with open(".bridge/start.sh", "w") as f:
        # TODO: detect this somehow, handle config
        app_path = "django_bridge.asgi:application"
        f.write(start_sh_template(app_path=app_path))

    with open(".bridge/render.yaml", "w") as f:
        f.write(
            render_yaml_template(
                service_name="django-bridge",
                database_name="django-bridge-db",
            )
        )

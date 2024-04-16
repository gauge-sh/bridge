from bridge.framework.base import Framework

template = """#!/usr/bin/env bash
# Exit on error
set -o errexit

# Get the directory of the current script.
DIR=$(dirname "$0")

# Use our Python script to install dependencies
INSTALL_DEPS_SCRIPT="$DIR/install_deps.py"
python "$INSTALL_DEPS_SCRIPT"

# Install additional dependencies
pip install gunicorn uvicorn psycopg-binary whitenoise[brotli]

# Collect static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
"""


def build_sh_template(framework: Framework) -> str:
    if framework != Framework.DJANGO:
        raise NotImplementedError(
            f"Unsupported framework for Render platform: {framework}"
        )
    return template.format()

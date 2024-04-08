#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Install additional dependencies
pip install gunicorn uvicorn psycopg-binary whitenoise[brotli]

# Collect static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

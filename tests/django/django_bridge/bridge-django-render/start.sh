#!/usr/bin/env bash
gunicorn django_bridge.custom_wsgi:application -w "${WEB_CONCURRENCY:-4}" -b 0.0.0.0:"$PORT" 

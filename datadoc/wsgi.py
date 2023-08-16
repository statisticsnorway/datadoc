"""Entrypoint for Gunicorn."""

from .app import get_app

datadoc_app = get_app()
server = datadoc_app.server

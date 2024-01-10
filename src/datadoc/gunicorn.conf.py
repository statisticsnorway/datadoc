"""Configuraion for the Gunicorn server."""

bind = "0.0.0.0:8050"
workers = 1
loglevel = "info"
preload = True

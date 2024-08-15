"""Configuration for the Gunicorn server."""
# TODO(@tilen1976: remove?)  # noqa: TD004, TD003
bind = "0.0.0.0:8050"
workers = 1
loglevel = "info"
preload = True

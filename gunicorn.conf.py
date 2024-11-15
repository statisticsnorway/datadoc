"""Configuration for the Gunicorn server."""

import sys

bind = "0.0.0.0:8050"
workers = 1
loglevel = "info"
preload = True

logconfig_dict = GUNICORN_LOG_CONFIG = {
    "handlers": {
        "console_stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "": {"handlers": ["console_stdout"], "level": "INFO", "propagate": False},
        "gunicorn": {
            "handlers": ["console_stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["console_stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.error": {
            "handlers": ["console_stdout"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console_stdout"],
    },
}

from __future__ import annotations

import logging.config
from typing import Any

from datadoc.config import get_log_formatter
from datadoc.config import get_log_level


def configure_logging(config: dict[str, Any] | None = None) -> None:
    """Configure logging for the application."""
    if not config:
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s",
                    "logger": "name",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "json": {
                    "()": "datadoc.logging_configuration.json_formatter.DatadocJSONFormatter",
                    "fmt_keys": {
                        "level": "levelname",
                        "message": "message",
                        "timestamp": "timestamp",
                        "logger": "name",
                        "module": "module",
                        "function": "funcName",
                        "line": "lineno",
                        "thread_name": "threadName",
                    },
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "level": get_log_level(),
                    "formatter": get_log_formatter(),
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "root": {
                    "level": get_log_level(),
                    "handlers": [
                        "stdout",
                    ],
                },
            },
        }

    logging.config.dictConfig(config)
    logging.getLogger("faker").setLevel(logging.ERROR)

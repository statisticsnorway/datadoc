from __future__ import annotations

import logging.config
import os
from typing import Any


def configure_logging(config: dict[str, Any] | None = None) -> None:
    """Configure logging for the application."""
    if not config:
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "format": "%(asctime)s %(levelname)s %(message)s",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                },
            },
            "loggers": {
                "": {"handlers": ["stdout"], "level": os.getenv("DATADOC_LOG_LEVEL")},
            },
        }

    logging.config.dictConfig(config)

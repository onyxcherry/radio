from datetime import time, timedelta
import logging
import logging.config
from typing import Final
from zoneinfo import ZoneInfo


from player.src.domain.types import Seconds


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)s %(module)s - "
            "%(funcName)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}


def get_logger(name: str) -> logging.Logger:
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(name)
    return logger


@dataclass(frozen=True)
class BreaksConfig:
    start_times: dict[time, Seconds]
    offset: timedelta
    timezone: timezone | ZoneInfo


@dataclass(frozen=True)
class Config:
    breaks: BreaksConfig

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


class BreaksConfig:
    START_TIMES: Final = {
        time(8, 30): Seconds(10 * 60),
        time(9, 25): Seconds(10 * 60),
        time(10, 20): Seconds(10 * 60),
        time(11, 15): Seconds(15 * 60),
        time(12, 15): Seconds(10 * 60),
        time(13, 10): Seconds(10 * 60),
        time(14, 5): Seconds(10 * 60),
        time(15, 00): Seconds(10 * 60),
    }
    OFFSET: Final = timedelta(seconds=17)
    TIMEZONE: Final = ZoneInfo("Europe/Warsaw")

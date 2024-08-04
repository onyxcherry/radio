from pydantic.dataclasses import dataclass
from datetime import time, timedelta, timezone
import logging
import logging.config
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import ConfigDict, field_validator


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


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class BreaksConfig:
    start_times: dict[time, Seconds]
    offset: timedelta
    timezone: timezone | ZoneInfo

    @field_validator("start_times")
    @classmethod
    def ensure_start_times_valid(cls, v: Any):
        if not isinstance(v, dict):
            raise ValueError("expected dict")
        if len(set(v.keys())) != len(v.keys()):
            raise ValueError("breaks times were duplicated")
        if sorted(list(v.keys())) != list(v.keys()):
            raise ValueError("expected breaks sorted by its start times")
        return v


@dataclass(frozen=True)
class Config:
    breaks: BreaksConfig

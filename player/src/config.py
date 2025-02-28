import json
import logging
import logging.config
from datetime import date, datetime, time, timedelta, tzinfo
from os import PathLike
from pathlib import Path
from typing import Annotated, Any, Optional, Self
from zoneinfo import ZoneInfo

import yaml
from jsonschema import ValidationError, validate
from pydantic import (
    BeforeValidator,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.types import Seconds

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


def load_config_from_yaml(
    config_path: Optional[PathLike] = None, schema_path: Optional[PathLike] = None
) -> dict:
    if schema_path is None:
        schema_path = Path(__file__).parent.parent.joinpath("config.schema.json")
    with open(schema_path, "r") as schema_file:
        schema = json.load(schema_file)

    if config_path is None:
        config_path = Path(__file__).parent.joinpath("config.yaml")
    with open(config_path, "r") as config_file:
        config_content = yaml.safe_load(config_file)

    try:
        validate(instance=config_content, schema=schema)
    except ValidationError as ex:
        raise ex
    else:
        return config_content


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class BreakData:
    start: time
    duration: Optional[Seconds] = None
    end: Optional[time] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def check_end_or_duration_and_set_the_other(self):
        if self.end is None and self.duration is None:
            raise ValueError("Either 'end' or 'duration' is required")
        if self.duration is None and self.end is not None:
            today = date.today()
            td = datetime.combine(today, self.end) - datetime.combine(today, self.start)
            self.duration = Seconds(int(td.total_seconds()))
        if self.duration is not None and self.end is None:
            today = date.today()
            end_dt = datetime.combine(today, self.start) + timedelta(
                seconds=self.duration
            )
            self.end = end_dt.time()
        return self

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return TypeAdapter(cls).validate_python(data)


def seconds_object_to_timedelta(data: Any) -> timedelta:
    if isinstance(data, timedelta):
        return data
    elif hasattr(data, "seconds") or (
        isinstance(data, dict) and data.get("seconds") is not None
    ):
        seconds = int(data["seconds"])
        return timedelta(seconds=seconds)
    raise ValidationError("Bad offset object, no seconds param")


def tzinfo_from_timezone_name(data: Any) -> tzinfo:
    if isinstance(data, tzinfo):
        return data
    return ZoneInfo(str(data))


SecondsTimedelta = Annotated[timedelta, BeforeValidator(seconds_object_to_timedelta)]

TzinfoFromName = Annotated[tzinfo, BeforeValidator(tzinfo_from_timezone_name)]


@dataclass(
    frozen=True, config=ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
)
class BreaksConfig:
    offset: SecondsTimedelta
    timezone: TzinfoFromName
    breaks: list[BreakData] = Field(validation_alias="list", serialization_alias="list")

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

    @classmethod
    def from_dict(cls, config: dict) -> Self:
        return TypeAdapter(cls).validate_python(config)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env", env_file_encoding="utf-8"
    )

    tracks_files_path: str = Field(
        str((Path(__file__).parent.parent / "data").absolute())
    )
    sqlalchemy_database_url: str = Field("sqlite:///./sql_app.db")
    broker_bootstrap_server: str = Field("localhost:19092")
    schema_registry_url: str = Field("http://localhost:18081")


@dataclass(frozen=True)
class Config:
    breaks: BreaksConfig


def config_dict_to_class(config: dict) -> Config:
    return TypeAdapter(Config).validate_python(config)

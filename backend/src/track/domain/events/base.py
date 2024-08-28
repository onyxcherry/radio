from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Any

from pydantic import AwareDatetime, BeforeValidator, ConfigDict, Field, PlainSerializer


def millis_to_timestamp(v: Any) -> datetime:
    if isinstance(v, int):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc)
    return v


def unix_epoch_date_to_date(v: Any) -> date:
    if isinstance(v, int):
        return date(1970, 1, 1) + timedelta(days=v)
    return v


MillisDatetime = Annotated[
    AwareDatetime,
    BeforeValidator(millis_to_timestamp),
    PlainSerializer(lambda dt: int(dt.timestamp() * 1000)),
]

DateFromUnixEpoch = Annotated[
    date,
    BeforeValidator(unix_epoch_date_to_date),
    PlainSerializer(lambda d: (d - date(1970, 1, 1)).days),
]


class Event:
    pass

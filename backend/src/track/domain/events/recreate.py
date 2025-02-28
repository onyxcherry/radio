from pydantic import TypeAdapter

from track.domain.events.base import Event
from track.domain.events.library import *  # noqa: F401, F403
from track.domain.events.playlist import *  # noqa: F401, F403


def parse_event(data: dict) -> Event:
    event_name = data.get("event_name") or data.get("name")
    if event_name is None:
        raise RuntimeError("No event name!")
    event = TypeAdapter(event_name).validate_python(data)
    return event

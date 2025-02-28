from pydantic import TypeAdapter

from domain.events.track import *  # noqa: F401, F403
from domain.events.track import Event


def parse_event(data: dict) -> Event:
    event_name = data.get("event_name") or data.get("name")
    if event_name is None:
        raise RuntimeError("No event name!")
    event = TypeAdapter(event_name).validate_python(data)
    return event

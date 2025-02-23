from pydantic import TypeAdapter
from domain.events.track import Event
from domain.events.track import *


def parse_event(data: dict) -> Event:
    event_name = data.get("event_name") or data.get("name")
    if event_name is None:
        raise RuntimeError("No event name!")
    event = TypeAdapter(event_name).validate_python(data)
    return event

from pydantic import RootModel
from track.domain.events.base import Event
from track.domain.events.library import *
from track.domain.events.playlist import *


def serialize_event(event: Event) -> str:
    return RootModel[type(event)](event).model_dump(by_alias=True)

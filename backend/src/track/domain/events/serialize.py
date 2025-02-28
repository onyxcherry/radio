from pydantic import RootModel

from track.domain.events.base import Event
from track.domain.events.library import *  # noqa: F401, F403
from track.domain.events.playlist import *  # noqa: F401, F403


def serialize_event(event: Event) -> str:
    return RootModel[type(event)](event).model_dump(by_alias=True, mode="json")

from pydantic import RootModel
from player.src.domain.events.base import Event


def serialize_event(event: Event) -> str:
    return RootModel[type(event)](event).model_dump_json()

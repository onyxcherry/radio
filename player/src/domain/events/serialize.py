from pydantic import RootModel
from domain.events.base import Event


def serialize_event(event: Event) -> str:
    return RootModel[type(event)](event).model_dump(by_alias=True)

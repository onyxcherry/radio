from re import Pattern
from typing import Optional
from track.application.interfaces.events import (
    ConsumerConnectionOptions,
    EventsConsumer,
    MessagesOptions,
)
from track.domain.events.base import Event
from track.infrastructure.messaging.schema_utils import SchemaRegistryConfig


class InMemoryEventsConsumer(EventsConsumer):
    def __init__(
        self,
        conn_options: Optional[ConsumerConnectionOptions] = None,
        msg_options: Optional[MessagesOptions] = None,
        schema_config: Optional[SchemaRegistryConfig] = None,
        test: bool = False,
    ) -> None:
        self._topics: list[str] = []
        self._messages: dict[str, list[Event]] = {}

    def subscribe(
        self, topics: str | list[str], pattern: Pattern | None = None
    ) -> None:
        if isinstance(topics, str):
            self._topics.append(topics)
        else:
            for topic in topics:
                self._topics.append(topic)

    def consume(self, limit: int) -> list[Event]:
        messages: list[Event] = []
        for topic in self._topics:
            topic_messages = self._messages.get(topic)
            if topic_messages is not None:
                messages.append(*topic_messages)
        return messages[:limit]

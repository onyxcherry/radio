from player.src.application.interfaces.events import (
    ConsumerConnectionOptions,
    ConsumerMessagesOptions,
    EventsConsumer,
)
from player.src.domain.events.base import Event
from player.src.infrastructure.messaging.schema_utils import SchemaRegistryConfig


class InMemoryEventsConsumer(EventsConsumer):
    def __init__(
        self,
        conn_options: ConsumerConnectionOptions,
        msg_options: ConsumerMessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        self._topic = schema_config.topic_name
        self._messages: dict[str, list[Event]] = {}

    def subscribe(self, topic: str) -> None:
        self._topic = topic

    def consume(self, limit: int) -> list[Event]:
        messages = self._messages.get(self._topic) or list()
        if len(messages) != limit:
            raise RuntimeError(f"Found {len(messages)} events, but limit is {limit}")
        self._messages = {}
        return messages

    def reset(self) -> None:
        self._messages = {}

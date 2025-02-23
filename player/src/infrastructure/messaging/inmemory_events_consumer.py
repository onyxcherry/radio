from kink import di
from player.src.application.interfaces.events import (
    ConsumerConnectionOptions,
    ConsumerMessagesOptions,
    EventsConsumer,
)
from player.src.domain.events.base import Event
from player.src.infrastructure.messaging.inmemory_events_helper import InMemoryEvents
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

    def subscribe(self, topic: str) -> None:
        self._topic = topic

    async def consume(self, limit: int) -> list[Event]:
        events_store = di[InMemoryEvents]
        messages = events_store.get_and_ack_for(self._topic, limit)
        if len(messages) != limit:
            raise RuntimeError(f"Found {len(messages)} events, but limit is {limit}")
        return messages

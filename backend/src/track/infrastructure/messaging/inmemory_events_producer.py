from typing import Optional
from track.application.interfaces.events import (
    EventsProducer,
    ProducerMessagesOptions,
    ProducerConnectionOptions,
)
from track.domain.events.base import Event
from track.infrastructure.messaging.schema_utils import SchemaRegistryConfig


class InMemoryEventsProducer(EventsProducer):
    def __init__(
        self,
        conn_options: ProducerConnectionOptions,
        msg_options: ProducerMessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        # topic name -> messages
        self._messages: dict[str, list[Event]] = {}
        self._topic_name = self._schema_config.topic_name
    def produce(self, message: Event) -> None:

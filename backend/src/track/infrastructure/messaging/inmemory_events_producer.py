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
        conn_options: Optional[ProducerConnectionOptions] = None,
        msg_options: Optional[ProducerMessagesOptions] = None,
        schema_config: Optional[SchemaRegistryConfig] = None,
        test: bool = False,
    ) -> None:
        # topic name -> messages
        self._messages: dict[str, list[Event]] = {}

    def produce(self, topic: str, message: Event) -> None:
        if topic not in self._messages:
            self._messages[topic] = []
        self._messages[topic].append(message)

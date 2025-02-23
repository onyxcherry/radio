from kink import di
from player.src.application.interfaces.events import (
    EventsProducer,
    ProducerMessagesOptions,
    ProducerConnectionOptions,
)
from player.src.domain.events.base import Event
from player.src.infrastructure.messaging.inmemory_events_helper import InMemoryEvents
from player.src.infrastructure.messaging.schema_utils import SchemaRegistryConfig


class InMemoryEventsProducer(EventsProducer):
    def __init__(
        self,
        conn_options: ProducerConnectionOptions,
        msg_options: ProducerMessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        # topic name -> messages
        self._schema_config = schema_config
        self._topic_name = self._schema_config.topic_name

    def produce(self, message: Event) -> None:
        events_store = di[InMemoryEvents]
        events_store.append(message, self._topic_name)

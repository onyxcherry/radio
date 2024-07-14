from re import Pattern
from typing import Optional

from confluent_kafka import Consumer
from track.domain.events.base import Event
from track.domain.events.utils.create import event_from_dict
from track.infrastructure.messaging.schema_utils import (
    SchemaRegistryConfig,
    fetch_schema,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer

from track.application.interfaces.events import (
    ConsumerConnectionOptions,
    EventsConsumer,
    MessagesOptions,
)
from confluent_kafka.serialization import SerializationContext, MessageField


class KafkaAvroEventsConsumer(EventsConsumer):
    def __init__(
        self,
        conn_options: ConsumerConnectionOptions,
        msg_options: MessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        consumer_conf = {
            "bootstrap.servers": conn_options.bootstrap_servers,
            "group.id": conn_options.group_id,
            "auto.offset.reset": "earliest",
        }
        self._consumer_conf = consumer_conf
        consumer = Consumer(consumer_conf)
        self._consumer = consumer
        self._schema_config = schema_config
        self._avro_deserializer = self._connect_schema_reg()

    def _connect_schema_reg(self):
        schema_reg_client, schema_str = fetch_schema(self._schema_config)
        avro_deserializer = AvroDeserializer(schema_reg_client, schema_str)
        return avro_deserializer

    def subscribe(
        self, topics: str | list[str] | None, pattern: Optional[Pattern] = None
    ) -> None:
        self._consumer.subscribe(topics or pattern)

    def consume(self, limit: int) -> Event:
        while True:
            msg = self._consumer.poll(0.0)
            if msg is None:
                continue

            result = self._avro_deserializer(
                msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
            )
            if result is not None:
                event_obj = event_from_dict(result)
                return event_obj

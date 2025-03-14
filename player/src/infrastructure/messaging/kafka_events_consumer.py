import asyncio
from typing import Literal, Optional

from confluent_kafka import OFFSET_BEGINNING, Consumer, TopicPartition
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import MessageField, SerializationContext

from application.interfaces.events import (
    ConsumerConnectionOptions,
    ConsumerMessagesOptions,
    EventsConsumer,
)
from config import get_logger
from domain.events.base import Event
from infrastructure.messaging.schema_utils import (
    SchemaRegistryConfig,
    create_client,
    fetch_schema,
)

logger = get_logger(__name__)


class KafkaAvroEventsConsumer(EventsConsumer):
    def __init__(
        self,
        conn_options: ConsumerConnectionOptions,
        msg_options: ConsumerMessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        consumer_conf = {
            "bootstrap.servers": conn_options.bootstrap_servers,
            "group.id": conn_options.group_id,
            "auto.offset.reset": "earliest",
        }
        self._consumer_conf = consumer_conf
        self._consumer = Consumer(consumer_conf)
        self._key_deserializer = msg_options.key_deserializer
        self._value_deserializer = msg_options.value_deserializer
        self._schema_config = schema_config
        self._schema_reg_client = create_client(self._schema_config)
        self.subscribe(self._schema_config.topic_name)
        self._avro_deserializer = self._create_avro_deserializer(
            schema_id=schema_config.schema_id, subject_name=schema_config.subject_name
        )
        self._topic: Optional[str] = None

    def _create_avro_deserializer(
        self, schema_id: int | Literal["latest"], subject_name: Optional[str]
    ) -> AvroDeserializer:
        schema_str = fetch_schema(
            client=self._schema_reg_client,
            schema_id=schema_id,
            subject_name=subject_name,
        )
        avro_deserializer = AvroDeserializer(
            self._schema_reg_client, schema_str=schema_str
        )
        return avro_deserializer

    def subscribe(self, topic: str) -> None:
        self._topic = topic
        tp = TopicPartition(topic, 0)
        self._consumer.assign([tp])

    def seek_beginning(self) -> None:
        assert self._topic is not None
        tp = TopicPartition(self._topic, 0, OFFSET_BEGINNING)
        self._consumer.seek(tp)

    async def consume(self, limit: int) -> list[Event]:
        results = []
        while len(results) != limit:
            msg = self._consumer.poll(0.01)
            if msg is None:
                await asyncio.sleep(0.01)
                continue

            result = self._avro_deserializer(
                msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
            )
            if result is not None:
                event_obj = self._value_deserializer(result)
                results.append(event_obj)
        return results

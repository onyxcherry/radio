from typing import Literal, Optional
from uuid import uuid4

from confluent_kafka import Producer
from confluent_kafka.schema_registry.avro import AvroSerializer

from confluent_kafka.serialization import SerializationContext, MessageField

from track.application.interfaces.events import (
    EventsProducer,
    ProducerConnectionOptions,
    ProducerMessagesOptions,
)
from track.domain.events.base import Event
from track.infrastructure.config import get_logger
from track.infrastructure.messaging.schema_utils import (
    SchemaRegistryConfig,
    create_client,
    fetch_schema,
)

logger = get_logger(__name__)


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.

        msg (Message): The message that was produced or failed.

    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """

    if err is not None:
        logger.warning(f"Delivery failed for record {msg.key()}: {err}")
        return
    logger.info(
        f"Record {msg.key()} successfully produced to {msg.topic()} "
        f"[{msg.partition()}] at offset {msg.offset()}"
    )
    logger.info(f"Message content is: {msg.value()}")


class KafkaAvroEventsProducer(EventsProducer):
    def __init__(
        self,
        conn_options: ProducerConnectionOptions,
        msg_options: ProducerMessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        producer_conf = {
            "bootstrap.servers": conn_options.bootstrap_servers,
            "client.id": conn_options.client_id,
        }
        self._producer_conf = producer_conf
        self._producer = Producer(producer_conf)
        self._partitioner = msg_options.partitioner
        self._key_serializer = msg_options.key_serializer
        self._value_serializer = msg_options.value_serializer
        self._schema_config = schema_config
        self._schema_reg_client = create_client(self._schema_config)
        self._avro_serializer = self._create_avro_serializer(
            schema_id=schema_config.schema_id, subject_name=schema_config.subject_name
        )

    def _serialize_event(self, obj: Event, ctx):
        return self._value_serializer(obj)

    def _create_avro_serializer(
        self, schema_id: int | Literal["latest"], subject_name: Optional[str]
    ) -> AvroSerializer:
        conf = {"auto.register.schemas": False}
        schema_str = fetch_schema(
            client=self._schema_reg_client,
            schema_id=schema_id,
            subject_name=subject_name,
        )
        avro_serializer = AvroSerializer(
            self._schema_reg_client,
            schema_str=schema_str,
            conf=conf,
            to_dict=self._serialize_event,
        )
        return avro_serializer

    def produce(self, message: Event) -> None:
        key = self._key_serializer(str(uuid4()))
        topic = self._schema_config.topic_name
        value = self._avro_serializer(
            message, SerializationContext(topic, MessageField.VALUE)
        )
        try:
            self._producer.produce(
                topic=topic,
                key=key,
                value=value,
                on_delivery=delivery_report,
            )
        except ValueError as ex:
            logger.exception(f"{ex=}")
            logger.error("Invalid input, discarding record...")

        self._producer.flush()

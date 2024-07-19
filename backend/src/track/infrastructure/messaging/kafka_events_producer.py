from datetime import date
from uuid import uuid4

from confluent_kafka import Producer
from track.domain.events.base import Event
from track.infrastructure.messaging.schema_utils import (
    SchemaRegistryConfig,
    fetch_schema,
)
from confluent_kafka.schema_registry.avro import AvroSerializer

from track.application.interfaces.events import (
    EventsProducer,
    MessagesOptions,
    ProducerConnectionOptions,
)
from confluent_kafka.serialization import (
    StringSerializer,
    SerializationContext,
    MessageField,
)


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
        print(f"Delivery failed for record {msg.key()}: {err}")
        return
    print(
        f"Record {msg.key()} successfully produced to {msg.topic()} "
        f"[{msg.partition()}] at offset {msg.offset()}"
    )


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, date):
        return obj.isoformat()
    else:
        return obj.__dict__


class KafkaAvroEventsProducer(EventsProducer):
    def __init__(
        self,
        conn_options: ProducerConnectionOptions,
        msg_options: MessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        producer_conf = {
            "bootstrap.servers": conn_options.bootstrap_servers,
            "client.id": conn_options.client_id,
            "auto.offset.reset": "earliest",
        }
        self._producer_conf = producer_conf
        producer = Producer(producer_conf)
        self._producer = producer
        self._schema_config = schema_config
        self._string_serializer = StringSerializer("utf_8")
        self._connect_schema_reg()
        self._avro_serializer = self._connect_schema_reg()

    def _connect_schema_reg(self) -> AvroSerializer:
        conf = {"auto.register.schemas": False}
        schema_reg_client, schema_str = fetch_schema(self._schema_config)
        avro_serializer = AvroSerializer(
            schema_reg_client, schema_str=schema_str, conf=conf
        )
        return avro_serializer

    def produce(self, message: Event) -> None:
        key = self._key_serializer(str(uuid4()))
        try:
            self._producer.produce(
                topic=topic,
                key=key,
                value=self._avro_serializer(
                    message, SerializationContext(topic, MessageField.VALUE)
                ),
                on_delivery=delivery_report,
            )
        except ValueError as ex:
            print(f"{ex=}")
            print("Invalid input, discarding record...")

        self._producer.flush()

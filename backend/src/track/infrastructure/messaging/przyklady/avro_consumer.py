import os

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer



def main():
    topic = "queue"
    schema_registry_conf = {"url": "http://localhost:18081"}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    consumer_conf = "localhost:19092"

    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    schema = schema_registry_client.get_schema(13)
    schema_str = schema.schema_str
    print(f"{schema_str=}")

    dict_to_user = None
    avro_deserializer = AvroDeserializer(
        schema_registry_client, schema_str
    )

    consumer_conf = {
        "bootstrap.servers": consumer_conf,
        "group.id": "consumer-1",
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            user = avro_deserializer(
                msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
            )
            if user is not None:
                # print(
                #     "User record {}: name: {}\n"
                #     "\tfavorite_number: {}\n"
                #     "\tfavorite_color: {}\n".format(
                #         msg.key(), user.name, user.favorite_number, user.favorite_color
                #     )
                # )
                print(f"Dostałem: {user=}")
        except KeyboardInterrupt:
            break

    consumer.close()

main()
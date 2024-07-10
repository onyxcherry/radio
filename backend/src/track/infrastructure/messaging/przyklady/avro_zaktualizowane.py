#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# A simple example demonstrating use of AvroSerializer.

from datetime import date
from time import sleep
from uuid import uuid4
import json
from confluent_kafka import Producer
from confluent_kafka.serialization import (
    StringSerializer,
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from track.domain.breaks import Breaks, PlayingTime
from track.domain.provided import Identifier, TrackProvidedIdentity
from track.domain.events.playlist import TrackAddedToPlaylist

obj = TrackAddedToPlaylist(
    identity=TrackProvidedIdentity(
        identifier=Identifier("ZDZiXmCl4pk"), provider="Youtube"
    ),
    when=PlayingTime(break_=Breaks.FIFTH, date_=date(2024, 3, 12)),
    waits_on_approval=True,
)
print(f"{obj=}")

value_schema = {
    "type": "record",
    "name": "app.wisniewski.radio.playlist",
    "fields": [
        {"name": "event_name", "type": "string"},
        {
            "name": "identity",
            "type": {
                "type": "record",
                "name": "app.wisniewski.radio.TrackProvidedIdentity",
                "fields": [
                    {"name": "provider", "type": "string"},
                    {"name": "identifier", "type": "string"},
                ],
            },
        },
        {
            "default": None,
            "name": "when",
            "type": [
                "null",
                {
                    "type": "record",
                    "name": "app.wisniewski.radio.PlayingTime",
                    "fields": [
                        {
                            "logicalType": "timestamp-millis",
                            "name": "date",
                            "type": "long",
                        },
                        {"name": "break", "type": "int"},
                    ],
                },
            ],
        },
        {"default": None, "name": "waits_on_approval", "type": ["null", "boolean"]},
        {"default": None, "name": "break", "type": ["null", "int"]},
        {
            "default": None,
            "name": "start",
            "type": ["null", {"logicalType": "timestamp-millis", "type": "long"}],
        },
        {
            "default": None,
            "name": "end",
            "type": ["null", {"logicalType": "timestamp-millis", "type": "long"}],
        },
        {"logicalType": "timestamp-millis", "name": "created", "type": "long"},
    ],
}


def json_serial(obj2):
    """JSON serializer for objects not serializable by default json code"""
    # print(f"{ctx=}")
    if isinstance(obj2, date):
        return obj2.isoformat()
    else:
        return obj2.__dict__
    raise TypeError("Type %s not serializable" % type(obj))


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
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print(
        "User record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


bb = {
    "identity": {"identifier": "ZDZiXmCl4pk", "provider": "Youtube"},
    "when": {"date": 738957, "break": 5},
    "waits_on_approval": True,
    "created": 1234566,
    "event_name": "TrackAddedToPlaylist",
}
aa = {
    "identity.identifier": "ZDZiXmCl4pk",
    "identity.provider": "Youtube",
    "date_": "2024-03-12",
    "break_": 5,
    "waits_on_approval": True,
    "created": "2024-07-10T18:27:43.116589+00:00",
}


def main():
    topic = "queue"
    schema_registry_conf = {"url": "http://localhost:18081"}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    conf = {"auto.register.schemas": False}
    schema_str = json.dumps(value_schema)
    avro_serializer = AvroSerializer(
        schema_registry_client,
        schema_str=schema_str,
        conf=conf,  # , to_dict=json_serial
    )

    string_serializer = StringSerializer("utf_8")

    producer_conf = {"bootstrap.servers": "localhost:19092"}

    producer = Producer(producer_conf)

    print("Producing user records to topic {}. ^C to exit.".format(topic))
    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)
        try:
            producer.produce(
                topic=topic,
                key=string_serializer(str(uuid4())),
                value=avro_serializer(
                    bb, SerializationContext(topic, MessageField.VALUE)
                ),
                on_delivery=delivery_report,
            )
            sleep(1)
        except KeyboardInterrupt:
            break
        except ValueError as ex:
            print(f"{ex=}")
            sleep(1)
            print("Invalid input, discarding record...")
            continue

    print("\nFlushing records...")
    producer.flush()


main()

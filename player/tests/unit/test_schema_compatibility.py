from datetime import date, datetime, timedelta, timezone
import io
from typing import Final
import fastavro
from fastavro.validation import validate
from pytest import fixture

from player.src.domain.events.track import (
    date_as_unix_epoch_date_int,
    datetime_as_millis_timestamp,
    millis_timestamp_as_datetime,
    unix_epoch_date_int_as_date,
)
from player.src.infrastructure.messaging.schema_utils import (
    SchemaRegistryConfig,
    create_client,
    fetch_schema,
)


@fixture
def sch_reg_client():
    schema_registry_config = SchemaRegistryConfig(
        url="http://localhost:18081",
        topic_name="queue",
        schema_id="latest",
        subject_name="queue-value",
    )
    client = create_client(schema_registry_config)
    return client


schema: Final = {
    "type": "record",
    "name": "app.wisniewski.radio.queue",
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
                            "name": "date",
                            "type": {"logicalType": "date", "type": "int"},
                        },
                        {"name": "break", "type": "int"},
                    ],
                },
            ],
        },
        {"default": None, "name": "duration", "type": ["null", "int"]},
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
        {
            "name": "created",
            "type": {"logicalType": "timestamp-millis", "type": "long"},
        },
    ],
}


fastavro.write.LOGICAL_WRITERS["int-date"] = date_as_unix_epoch_date_int
fastavro.read.LOGICAL_READERS["int-date"] = unix_epoch_date_int_as_date
fastavro.write.LOGICAL_WRITERS["long-timestamp-millis"] = datetime_as_millis_timestamp
fastavro.read.LOGICAL_READERS["long-timestamp-millis"] = millis_timestamp_as_datetime


def test_fetches_schema_of_specific_version(sch_reg_client):
    schema = fetch_schema(client=sch_reg_client, schema_id=1, subject_name=None)
    assert '"namespace":"app.wisniewski.radio"' in schema


def test_fetches_latest_schema_of_subject(sch_reg_client):
    schema = fetch_schema(
        client=sch_reg_client, schema_id="latest", subject_name="queue-value"
    )
    assert '"namespace":"app.wisniewski.radio"' in schema


def test_schema_compatibility():
    record = {
        "identity": {"identifier": "bb", "provider": "file"},
        "when": {"date": date(2024, 8, 19), "break": 1},
        "duration": 42,
        "waits_on_approval": False,
        "created": datetime(2024, 7, 11, 7, 12, 42, tzinfo=timezone.utc),
        "event_name": "TrackAddedToPlaylist",
    }
    result = validate(record, schema, strict=True)
    assert result is True

    bio = io.BytesIO()
    writer_schema = fastavro.parse_schema(schema)
    fastavro.writer(bio, writer_schema, [record])

    bio.seek(0)

    events_read = list(fastavro.reader(bio))
    assert events_read[0] == {
        "identity": {"provider": "file", "identifier": "bb"},
        "when": {"date": date(2024, 8, 19), "break": 1},
        "duration": 42,
        "waits_on_approval": False,
        "created": datetime(2024, 7, 11, 7, 12, 42, tzinfo=timezone.utc),
        "event_name": "TrackAddedToPlaylist",
        "break": None,
        "start": None,
        "end": None,
    }

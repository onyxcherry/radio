from datetime import datetime, timedelta, timezone
from kink import di
import pytest

from player.src.domain.breaks import Breaks
from player.src.domain.entities import TrackProvidedIdentity
from player.src.domain.events.serialize import serialize_event
from player.src.domain.events.recreate import parse_event
from player.src.domain.events.track import TrackPlayed
from player.src.domain.types import Identifier
from player.src.infrastructure.messaging.types import (
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)


@pytest.fixture
def reset(reset_events_fixt):
    pass


def test_parses_event_from_dict_with_iso_datetimes():
    dt_str = "2024-08-05T18:34:13.033391Z"
    dict_data = {
        "identity": {"identifier": "aa", "provider": "Youtube"},
        "break": 1,
        "start": dt_str,
        "end": dt_str,
        "created": dt_str,
        "name": "TrackPlayed",
    }
    dt = datetime(2024, 8, 5, 18, 34, 13, 33391, tzinfo=timezone.utc)
    assert parse_event(dict_data) == TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=1,
        start=dt,
        end=dt,
        created=dt,
    )


def test_parses_event_from_dict_with_timestamp_millis_datetimes():
    millis_timestamp = 1722882853033
    dict_data = {
        "identity": {"identifier": "aa", "provider": "Youtube"},
        "break": 1,
        "start": millis_timestamp,
        "end": millis_timestamp,
        "created": millis_timestamp,
        "event_name": "TrackPlayed",
    }
    dt = datetime(2024, 8, 5, 18, 34, 13, 33000, tzinfo=timezone.utc)
    assert parse_event(dict_data) == TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=1,
        start=dt,
        end=dt,
        created=dt,
    )


def test_serializes_event():
    dt = datetime(2024, 8, 5, 18, 34, 13, 33391, tzinfo=timezone.utc)
    event = TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=1,
        start=dt,
        end=dt,
        created=dt,
    )
    millis_timestamp = 1722882853033
    assert int(dt.timestamp() * 1000) == millis_timestamp
    expected = {
        "identity": {"identifier": "aa", "provider": "Youtube"},
        "break": 1,
        "start": millis_timestamp,
        "end": millis_timestamp,
        "created": millis_timestamp,
        "event_name": "TrackPlayed",
    }
    assert serialize_event(event) == expected


def test_consume_produced_event(reset):
    events_producer = di[PlaylistEventsProducer]
    events_consumer = di[PlaylistEventsConsumer]

    event_break = di[Breaks].as_list()[0]
    event = TrackPlayed(
        identity=TrackProvidedIdentity(
            identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
        ),
        break_=event_break.ordinal,
        start=event_break.start,
        end=event_break.end,
        created=event_break.end + timedelta(seconds=1),
    )
    events_producer.produce(event)

    assert events_consumer.consume(1)[0] == event

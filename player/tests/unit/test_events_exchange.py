from datetime import date, datetime, timedelta, timezone
from kink import di
import pytest

from player.src.domain.breaks import Breaks
from player.src.domain.entities import TrackProvidedIdentity
from player.src.domain.events.serialize import serialize_event
from player.src.domain.events.recreate import parse_event
from player.src.domain.events.track import (
    PlayingTime,
    TrackAddedToPlaylist,
    TrackPlayed,
)
from player.src.domain.types import Identifier, Seconds
from player.src.infrastructure.messaging.types import (
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)


@pytest.fixture
def reset(reset_events_fixt):
    pass


def test_parses_event_from_dict_with_unix_epoch_date_field():
    dict_data = {
        "identity": {"identifier": "bb", "provider": "file"},
        "when": {"date": 19954, "break": 1},
        "duration": 42,
        "waits_on_approval": False,
        "created": 1720681962000,
        "event_name": "TrackAddedToPlaylist",
    }
    event = TrackAddedToPlaylist(
        identity=TrackProvidedIdentity(identifier=Identifier("bb"), provider="file"),
        when=PlayingTime(break_=1, date_=date(2024, 8, 19)),
        duration=Seconds(42),
        waits_on_approval=False,
        created=datetime(2024, 7, 11, 7, 12, 42, tzinfo=timezone.utc),
    )
    assert parse_event(dict_data) == event


def test_parses_event_from_dict_with_iso_date_field():
    dict_data = {
        "identity": {"identifier": "bb", "provider": "file"},
        "when": {"date": "2024-08-19", "break": 1},
        "duration": 42,
        "waits_on_approval": False,
        "created": 1720681962000,
        "event_name": "TrackAddedToPlaylist",
    }
    event = TrackAddedToPlaylist(
        identity=TrackProvidedIdentity(identifier=Identifier("bb"), provider="file"),
        when=PlayingTime(break_=1, date_=date(2024, 8, 19)),
        duration=Seconds(42),
        waits_on_approval=False,
        created=datetime(2024, 7, 11, 7, 12, 42, tzinfo=timezone.utc),
    )
    assert parse_event(dict_data) == event


def test_parses_event_from_dict_with_iso_datetimes_fields():
    dt_str = "2024-08-05T18:34:13.033391Z"
    dict_data = {
        "identity": {"identifier": "aa", "provider": "Youtube"},
        "break": 1,
        "start": dt_str,
        "end": dt_str,
        "created": dt_str,
        "event_name": "TrackPlayed",
    }
    dt = datetime(2024, 8, 5, 18, 34, 13, 33391, tzinfo=timezone.utc)
    assert parse_event(dict_data) == TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=1,
        start=dt,
        end=dt,
        created=dt,
    )


def test_parses_event_from_dict_with_timestamp_millis_datetimes_fields():
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


def test_serializes_event_with_timestamp_millis():
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


def test_serializes_event_with_unix_epoch_date():
    event = TrackAddedToPlaylist(
        identity=TrackProvidedIdentity(identifier=Identifier("bb"), provider="file"),
        when=PlayingTime(break_=1, date_=date(2024, 8, 19)),
        duration=Seconds(42),
        waits_on_approval=False,
        created=datetime(2024, 7, 11, 7, 12, 42, tzinfo=timezone.utc),
    )
    expected = {
        "identity": {"identifier": "bb", "provider": "file"},
        "when": {"date": 19954, "break": 1},
        "duration": 42,
        "waits_on_approval": False,
        "created": 1720681962000,
        "event_name": "TrackAddedToPlaylist",
    }
    assert serialize_event(event) == expected


@pytest.mark.asyncio
async def test_consume_produced_events(reset):
    events_producer = di[PlaylistEventsProducer]
    events_consumer = di[PlaylistEventsConsumer]

    identity = TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    )
    event_break = di[Breaks].as_list()[0]
    event1 = TrackPlayed(
        identity=identity,
        break_=event_break.ordinal,
        start=event_break.start,
        end=event_break.end,
        created=event_break.end + timedelta(seconds=1),
    )
    event2 = TrackAddedToPlaylist(
        identity=identity,
        when=PlayingTime(date_=event_break.date, break_=event_break.ordinal),
        duration=Seconds(42),
        waits_on_approval=False,
        created=event_break.end + timedelta(seconds=43),
    )
    events_producer.produce(event1)
    events_producer.produce(event2)

    consumed_events = await events_consumer.consume(2)
    assert consumed_events[0] == event1
    assert consumed_events[1] == event2

from datetime import date, datetime, timedelta, timezone
from typing import Final

from kink import di

from config import Config
from track.domain.breaks import Breaks, PlayingTime
from track.domain.events.playlist import TrackAddedToPlaylist, TrackPlayed
from track.domain.events.recreate import parse_event
from track.domain.events.serialize import serialize_event
from track.domain.provided import Identifier, Seconds, TrackProvidedIdentity
from track.infrastructure.messaging.types import (
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)

config: Final = di[Config]


def test_parses_event_from_dict_with_unix_epoch_date_field():
    dict_data = {
        "identity": {"identifier": "bb", "provider": "file"},
        "when": {"date": 19954, "break": 1},
        "duration": 42,
        "waits_on_approval": False,
        "created": 1720681962000,
        "event_name": "TrackAddedToPlaylist",
    }
    ident = TrackProvidedIdentity(identifier=Identifier("bb"), provider="file")
    pt = PlayingTime(break_=Breaks.FIRST, date_=date(2024, 8, 19))
    TrackAddedToPlaylist(
        ident,
        pt,
        Seconds(42),
        False,
        datetime(2024, 7, 11, 7, 12, 42, tzinfo=timezone.utc),
    )
    event = TrackAddedToPlaylist(
        identity=ident,
        when=pt,
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
        when=PlayingTime(break_=Breaks.FIRST, date_=date(2024, 8, 19)),
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
    w = TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=Breaks.FIRST,
        start=dt,
        end=dt,
        created=dt,
    )
    assert parse_event(dict_data) == w


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
        break_=Breaks.FIRST,
        start=dt,
        end=dt,
        created=dt,
    )


def test_serializes_event_with_timestamp_millis():
    dt = datetime(2024, 8, 5, 18, 34, 13, 33391, tzinfo=timezone.utc)
    event = TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=Breaks.FIRST,
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
        when=PlayingTime(break_=Breaks.FIRST, date_=date(2024, 8, 19)),
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


def test_consume_produced_events(reset_events_fixt):
    events_producer = di[PlaylistEventsProducer]
    events_consumer = di[PlaylistEventsConsumer]

    identity = TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    )
    event_pt = PlayingTime(date(2024, 7, 11), Breaks.FIRST)
    break_ = config.breaks.breaks[event_pt.break_.get_number_from_zero_of()]
    assert break_ is not None
    assert break_.end is not None
    break_end = datetime.combine(event_pt.date_, break_.end, tzinfo=timezone.utc)
    event1 = TrackPlayed(
        identity=identity,
        break_=event_pt.break_,
        start=datetime.combine(event_pt.date_, break_.start, tzinfo=timezone.utc),
        end=break_end,
        created=break_end + timedelta(seconds=1),
    )
    event2 = TrackAddedToPlaylist(
        identity=identity,
        when=PlayingTime(date_=event_pt.date_, break_=event_pt.break_),
        duration=Seconds(42),
        waits_on_approval=False,
        created=break_end + timedelta(seconds=43),
    )
    events_producer.produce(event1)
    events_producer.produce(event2)

    consumed_events = events_consumer.consume(2)
    assert consumed_events[0] == event1
    assert consumed_events[1] == event2

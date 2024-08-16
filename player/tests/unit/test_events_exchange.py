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


def test_parses_event_from_dict():
    dict_data = {
        "identity": {"identifier": "aa", "provider": "Youtube"},
        "break_": 1,
        "start": "2024-08-05T20:34:13.033385",
        "end": "2024-08-05T18:34:13.033391Z",
        "created": "2024-08-05T20:34:13.033396",
        "name": "TrackPlayed",
    }
    assert parse_event(dict_data) == TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=1,
        start=datetime(2024, 8, 5, 20, 34, 13, 33385),
        end=datetime(2024, 8, 5, 18, 34, 13, 33391, tzinfo=timezone.utc),
        created=datetime(2024, 8, 5, 20, 34, 13, 33396),
    )


def test_serializes_event():
    event = TrackPlayed(
        identity=TrackProvidedIdentity(identifier=Identifier("aa"), provider="Youtube"),
        break_=1,
        start=datetime(2024, 8, 5, 20, 34, 13, 33385),
        end=datetime(2024, 8, 5, 18, 34, 13, 33391, tzinfo=timezone.utc),
        created=datetime(2024, 8, 5, 20, 34, 13, 33396),
    )
    expected = (
        '{"identity":{"identifier":"aa","provider":"Youtube"},"break_":1,'
        '"start":"2024-08-05T20:34:13.033385","end":"2024-08-05T18:34:13.033391Z",'
        '"created":"2024-08-05T20:34:13.033396","name":"TrackPlayed"}'
    )
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

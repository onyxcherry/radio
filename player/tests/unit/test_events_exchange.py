from datetime import timedelta
from kink import di
import pytest

from player.src.domain.breaks import Breaks
from player.src.domain.entities import TrackProvidedIdentity
from player.src.domain.events.track import TrackPlayed
from player.src.domain.types import Identifier
from player.src.infrastructure.messaging.types import (
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)


@pytest.fixture(autouse=True)
def reset(reset_events_fixt):
    pass


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

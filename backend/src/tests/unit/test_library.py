from typing import Sequence
from kink import di
from pytest import fixture
from tests.unit.fixtures.events import reset_events, provide_config
from track.infrastructure.messaging.types import LibraryEventsConsumer
from tests.helpers.messaging import sync_messages_from_producer_to_consumer
from building_blocks.clock import Clock
from track.domain.events.library import (
    TrackAccepted,
    TrackAddedToLibrary,
    TrackRejected,
)
from tests.unit.data import ACCEPTED_TRACKS, NEW_TRACKS, PENDING_APPROVAL_TRACKS
from track.application.library import Library
from track.domain.entities import Status
from tests.helpers.dt import fixed_dt


library = di[Library]
library_repo = library._library_repository
events_consumer = di[LibraryEventsConsumer]
events_consumer.subscribe(library._events_topic)
events_producer = library._events_producer
clock = di[Clock]


_realmsgbroker: bool


def sync_messages():
    sync_messages_from_producer_to_consumer(
        events_producer, events_consumer, real_msg_broker=_realmsgbroker
    )


@fixture(autouse=True)
def reset(provide_config):
    global _realmsgbroker
    _realmsgbroker = provide_config

    library_repo.delete_all()

    events_handlers: Sequence = [events_producer, events_consumer]
    reset_events(_realmsgbroker, events_handlers)

    yield

    library_repo.delete_all()


@fixture()
def tracks_one_accepted(reset):
    library_repo.add(PENDING_APPROVAL_TRACKS[0])
    library_repo.add(ACCEPTED_TRACKS[0])


def test_new_track_has_pending_approval_state():
    track = NEW_TRACKS[0]
    library.add(track)
    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.PENDING_APPROVAL
    sync_messages()
    expected_event = TrackAddedToLibrary(identity=track.identity, created=fixed_dt)
    assert expected_event in events_consumer.consume(1)





def test_filters_tracks_by_status(tracks_one_accepted):
    tracks_filtered = library.filter_by_statuses(
        [Status.PENDING_APPROVAL, Status.ACCEPTED]
    )
    assert len(tracks_filtered) == 2
    assert len(library.filter_by_statuses([Status.PENDING_APPROVAL])) == 1

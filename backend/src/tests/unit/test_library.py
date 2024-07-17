from datetime import datetime
from kink import di
from pytest import fixture
from tests.conftest import sync_messages_from_producer_to_consumer
from building_blocks.clock import Clock
from track.domain.events.library import (
    TrackAccepted,
    TrackAddedToLibrary,
    TrackRejected,
)
from track.domain.provided import Identifier, TrackProvidedIdentity
from track.application.interfaces.events import EventsConsumer
from tests.unit.data import ACCEPTED_TRACKS, NEW_TRACKS, PENDING_APPROVAL_TRACKS
from track.application.library import Library
from track.domain.entities import Status


library = di[Library]
events_consumer = di[EventsConsumer]
events_consumer.subscribe(library._events_topic)
events_producer = library._events_producer
clock = di[Clock]

fixed_dt = datetime(2024, 7, 16, 14, 19, 21)


def sync_messages():
    sync_messages_from_producer_to_consumer(events_producer, events_consumer)


@fixture(autouse=True)
def reset():
    library_repo = library._library_repository
    library_repo.delete_all()

    yield

    library_repo.delete_all()


@fixture()
def tracks_one_accepted(reset):
    library_repo = library._library_repository
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
    assert expected_event in events_consumer.consume(10)


def test_accept_track(tracks_one_accepted):
    track = PENDING_APPROVAL_TRACKS[0]
    library.accept(track.identity)

    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.ACCEPTED
    sync_messages()
    expected_event = TrackAccepted(
        identity=track.identity,
        previous_status=Status.PENDING_APPROVAL,
        created=fixed_dt,
    )
    assert expected_event in events_consumer.consume(10)


def test_reject_track(tracks_one_accepted):
    track = PENDING_APPROVAL_TRACKS[0]

    library.reject(track.identity)

    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.REJECTED
    sync_messages()
    expected_event = TrackRejected(
        identity=track.identity,
        previous_status=Status.PENDING_APPROVAL,
        created=fixed_dt,
    )
    assert expected_event in events_consumer.consume(10)


def test_filters_tracks_by_status(tracks_one_accepted):
    tracks_filtered = library.filter_by_statuses(
        [Status.PENDING_APPROVAL, Status.ACCEPTED]
    )
    assert len(tracks_filtered) == 2
    assert len(library.filter_by_statuses([Status.PENDING_APPROVAL])) == 1

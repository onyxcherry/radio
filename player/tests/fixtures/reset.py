from kink import di
import pytest

from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository
from player.tests.helpers.messaging import reset_events


@pytest.fixture(scope="function")
def reset_events_fixt():
    reset_events()

    yield

    reset_events()


@pytest.fixture(scope="function")
def reset_db_fixt():
    scheduled_tracks_repo = di[ScheduledTracksRepository]
    scheduled_tracks_repo.delete_all()

    yield

    scheduled_tracks_repo.delete_all()

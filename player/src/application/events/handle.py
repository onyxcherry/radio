from datetime import date, datetime
from typing import Any

from building_blocks.clock import Clock
from config import get_logger
from domain.breaks import Breaks
from domain.entities import TrackToSchedule
from domain.events.track import (
    Event,
    TrackAddedToPlaylist,
    TrackDeletedFromPlaylist,
)
from domain.repositories.scheduled_tracks import ScheduledTracksRepository
from domain.types import Seconds

logger = get_logger(__name__)

# assumptions:
# 1. events are ordered at least per topic (hence per track)
# TODO: configure partitioner
# 2.


class EventHandler:
    def __init__(
        self,
        breaks: Breaks,
        scheduled_tracks_repo: ScheduledTracksRepository,
        clock: Clock,
    ) -> None:
        self._breaks = breaks
        self._schtr_repo = scheduled_tracks_repo
        self._clock = clock

    def check_event_refers_to_the_past(self, when: date | datetime) -> bool:
        if when < self._clock.get_current_date():
            return True
        return False

    def handle_event(
        self,
        event: Event | Any,
    ) -> None:
        if not isinstance(event, Event):
            logger.warning(f"Not known event: {event}")

        match event:
            case TrackAddedToPlaylist() as added_to_playlist if (
                added_to_playlist.waits_on_approval is False
            ):
                break_ = self._breaks.on_day_of_ordinal(
                    added_to_playlist.when.date_, added_to_playlist.when.break_
                )
                assert break_ is not None
                to_schedule = TrackToSchedule(
                    identity=added_to_playlist.identity,
                    break_=break_,
                    duration=Seconds(
                        min(
                            added_to_playlist.duration,
                            break_.duration,
                        )
                    ),
                )
                result = self._schtr_repo.insert_or_update(to_schedule)
                if result.last_changed < added_to_playlist.created:
                    logger.info(
                        "Event doesn't change track's state. "
                        "May have had been applied before"
                    )
                else:
                    logger.info(f"Scheduled track {to_schedule}")

            case TrackDeletedFromPlaylist() as deleted_from_playlist:
                scheduled = self._schtr_repo.get_track_on(
                    identity=deleted_from_playlist.identity,
                    date_=deleted_from_playlist.when.date_,
                    break_=deleted_from_playlist.when.break_,
                )
                if scheduled is None:
                    logger.info("No track is scheduled")
                    return

                result = self._schtr_repo.delete(scheduled)
                if result is None:
                    logger.info("No track was deleted when handling event")
                else:
                    logger.info(f"Deleted {result}")

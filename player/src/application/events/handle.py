from datetime import date, datetime
from typing import Any

from player.src.building_blocks.clock import Clock
from player.src.config import get_logger
from player.src.domain.breaks import Breaks
from player.src.domain.entities import TrackToSchedule
from player.src.domain.events.track import (
    Event,
    TrackAddedToPlaylist,
    TrackDeletedFromPlaylist,
)
from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository

logger = get_logger(__name__)

# assumptions:
# 1. events are ordered at least per topic (hence per track) TODO: configure partitioner
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
        event: Any,
    ) -> None:
        if not isinstance(event, Event):
            raise RuntimeError("Not known event!")

        match event:
            case (
                TrackAddedToPlaylist() as added_to_playlist
            ) if added_to_playlist.waits_on_approval is False:
                break_, duration = self._breaks.lookup_details(
                    added_to_playlist.when.date_,
                    added_to_playlist.when.break_,
                )
                to_schedule = TrackToSchedule(
                    identity=added_to_playlist.identity,
                    break_=break_,
                    duration=duration,
                )
                result = self._schtr_repo.insert_or_update(to_schedule)
                if result.last_changed < added_to_playlist.created:
                    logger.info(
                        "Event doesn't change track's state. May have had been applied before"
                    )

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
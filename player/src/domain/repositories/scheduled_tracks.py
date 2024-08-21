from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from player.src.domain.breaks import Break
from player.src.domain.entities import (
    ScheduledTrack,
    TrackProvidedIdentity,
    TrackToSchedule,
)


class ScheduledTracksRepository(ABC):
    @abstractmethod
    def get_track_on(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[int] = None,
    ) -> Optional[ScheduledTrack]:
        pass

    @abstractmethod
    def get_all(
        self,
        date_: date,
        break_: Optional[int] = None,
        played: Optional[bool] = None,
    ) -> list[ScheduledTrack]:
        pass

    @abstractmethod
    def insert(self, track: TrackToSchedule) -> ScheduledTrack:
        pass

    @abstractmethod
    def update(self, track: ScheduledTrack) -> ScheduledTrack:
        pass

    @abstractmethod
    def insert_or_update(self, track: TrackToSchedule | ScheduledTrack) -> ScheduledTrack:
        pass

    @abstractmethod
    def delete(self, track: ScheduledTrack) -> Optional[ScheduledTrack]:
        pass

    @abstractmethod
    def delete_all(self) -> int:
        pass

    @abstractmethod
    def delete_all_with_identity(self, identity: TrackProvidedIdentity) -> int:
        pass

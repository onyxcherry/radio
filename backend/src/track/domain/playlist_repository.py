from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from track.domain.breaks import Breaks
from track.domain.entities import TrackQueued, TrackToQueue, TrackUnqueued
from track.domain.provided import Seconds, TrackProvidedIdentity


class PlaylistRepository(ABC):
    @abstractmethod
    def get_track_on(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> Optional[TrackQueued]:
        pass

    @abstractmethod
    def get_all(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> list[TrackQueued]:
        pass

    @abstractmethod
    def get_all_by_identity(self, identity: TrackProvidedIdentity) -> list[TrackQueued]:
        pass

    @abstractmethod
    def count_on(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> int:
        pass

    @abstractmethod
    def sum_durations_on(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> Seconds:
        pass

    @abstractmethod
    def insert(self, track: TrackToQueue) -> TrackQueued:
        pass

    @abstractmethod
    def update(self, track: TrackQueued) -> TrackQueued:
        pass

    @abstractmethod
    def delete(self, track: TrackQueued) -> Optional[TrackQueued]:
        pass

    @abstractmethod
    def delete_all(self) -> int:
        pass

    @abstractmethod
    def delete_all_with_identity(
        self, identity: TrackProvidedIdentity
    ) -> list[TrackUnqueued]:
        pass

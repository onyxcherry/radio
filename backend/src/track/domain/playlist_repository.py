from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from track.domain.breaks import Breaks

from track.domain.entities import TrackQueued
from track.domain.provided import (
    Identifier,
    ProviderName,
    Seconds,
    TrackUrl,
)


class PlaylistRepository(ABC):
    @abstractmethod
    def get_track_on(
        self,
        provider: ProviderName,
        identifier: Identifier,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> Optional[TrackQueued]:
        pass

    @abstractmethod
    def get_all_on(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> list[TrackQueued]:
        pass

    @abstractmethod
    def filter_on_by(
        self, track_url: TrackUrl, date_: date, conditions
    ) -> list[TrackQueued]:
        pass

    @abstractmethod
    def count_on(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> int:
        pass

    @abstractmethod
    def sum_durations_on(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> Seconds:
        pass

    @abstractmethod
    def save(self, track: TrackQueued) -> TrackQueued:
        pass

    @abstractmethod
    def delete(self, track: TrackQueued) -> TrackQueued:
        pass

from abc import ABC, abstractmethod
from typing import Optional
from backend.src.track.domain.status import Status
from track.application.dto import TrackEntity

from track.domain.track import TrackUrl


class LibraryRepository(ABC):
    @abstractmethod
    def get(self, track_url: TrackUrl) -> Optional[TrackEntity]:
        pass

    @abstractmethod
    def filter_by_statuses(self, statuses: list[Status]) -> list[TrackEntity]:
        pass

    @abstractmethod
    def add(self, track: TrackEntity) -> TrackEntity:
        pass

    @abstractmethod
    def update(self, track: TrackEntity) -> TrackEntity:
        pass

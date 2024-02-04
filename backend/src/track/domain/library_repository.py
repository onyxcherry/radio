from abc import ABC, abstractmethod
from typing import Optional
from track.application.dto import TrackEntity

from track.domain.track import TrackUrl


class LibraryRepository(ABC):
    @abstractmethod
    def get(self, track_url: TrackUrl) -> Optional[TrackEntity]:
        pass

    @abstractmethod
    def add(self, track: TrackEntity) -> None:
        pass

    @abstractmethod
    def update(self, track: TrackEntity) -> None:
        pass

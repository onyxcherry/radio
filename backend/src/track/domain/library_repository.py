from abc import ABC, abstractmethod
from typing import Optional
from track.domain.entities import Status, TrackInLibrary

from track.domain.provided import TrackProvidedIdentity


class LibraryRepository(ABC):
    @abstractmethod
    def get(self, identity: TrackProvidedIdentity) -> Optional[TrackInLibrary]:
        pass

    @abstractmethod
    def filter_by_statuses(
        self,
        statuses: list[Status],
    ) -> list[TrackInLibrary]:
        pass

    @abstractmethod
    def add(self, track: TrackInLibrary) -> TrackInLibrary:
        pass

    @abstractmethod
    def update(self, track: TrackInLibrary) -> TrackInLibrary:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass

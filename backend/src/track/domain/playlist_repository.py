from abc import ABC, abstractmethod
from datetime import date
from track.application.dto import TrackQueued, TrackRequestedAt

from track.domain.track import TrackUrl


class PlaylistRepository(ABC):
    @abstractmethod
    def get_on(self, track_url: TrackUrl, date_: date) -> list[TrackQueued]:
        pass

    @abstractmethod
    def filter_on_by(
        self, track_url: TrackUrl, date_: date, conditions
    ) -> list[TrackQueued]:
        pass

    @abstractmethod
    def save(self, track: TrackQueued) -> None:
        pass

    @abstractmethod
    def delete(self, track: TrackQueued) -> None:
        pass

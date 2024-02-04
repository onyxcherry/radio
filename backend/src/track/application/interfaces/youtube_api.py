from abc import ABC, abstractmethod

from track.domain.track import TrackId


class YoutubeAPIInterface(ABC):
    @staticmethod
    @abstractmethod
    def get_api_part(track_id: TrackId, part: str) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def get_channel_info(channel_id: str) -> dict:
        pass

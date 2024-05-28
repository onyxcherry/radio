from abc import ABC, abstractmethod

from track.domain.provided import Identifier


class YoutubeAPIInterface(ABC):
    @staticmethod
    @abstractmethod
    def get_api_part(track_id: Identifier, part: str) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def get_channel_info(channel_id: str) -> dict:
        pass

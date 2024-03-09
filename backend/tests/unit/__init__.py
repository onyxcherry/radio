from kink import di
from src.track.application.interfaces.youtube_api import YoutubeAPIInterface
from src.track.infrastructure.youtube_api import YoutubeAPI


def boostrap_di() -> None:
    di[YoutubeAPIInterface] = YoutubeAPI

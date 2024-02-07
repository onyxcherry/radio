from typing import Any, Type
from urllib.parse import urlparse, unquote

from track.infrastructure.youtube_api import YoutubeAPI
from track.domain.errors import TrackIdentifierError
from track.domain.status import ErrorMessages
from track.domain.providers.youtube import (
    ORIGINS as YoutubeOrigins,
    YoutubeTrackProvider,
)
from track.domain.track import TrackProvider, TrackUrl

DEFAULT_API_IMPLS: dict[Type[TrackProvider], Any] = {
    YoutubeTrackProvider: YoutubeAPI,
}


class TrackBuilder:
    @staticmethod
    def normalize(url: str) -> TrackUrl:
        if not isinstance(url, str):
            raise TypeError(f"Passed {type(url)} type, expected 'str'")

        url = unquote(url)
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return TrackUrl(url)

    @staticmethod
    def _extract_netloc(url: TrackUrl) -> str:
        parsed = urlparse(url)
        netloc = parsed.netloc.split("@")[-1].split(":")[0]
        return netloc

    @staticmethod
    def _match_provider(domain: str) -> Type[TrackProvider]:
        if domain in YoutubeOrigins:
            return YoutubeTrackProvider
        else:
            raise TrackIdentifierError(ErrorMessages.UNKNOWN_PROVIDER)

    @classmethod
    def build(cls, url: str):
        track_url = cls.normalize(url)
        netloc = cls._extract_netloc(track_url)
        provider = cls._match_provider(netloc)
        # ZAMIENIĆ NA DEPENDENCY INJECTION
        default_provider_api_impl = DEFAULT_API_IMPLS[provider]
        # jakie mamy gwarancje co do parametru track_url?
        # 1. jest poprawnym urlem
        # 2. nie jest id, a urlem
        return provider(track_url, default_provider_api_impl)

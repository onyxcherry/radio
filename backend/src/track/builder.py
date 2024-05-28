from typing import Any, Type
from urllib.parse import urlparse, unquote

from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.domain.errors import TrackIdentifierError
from track.domain.errors import ErrorMessages
from track.domain.providers.youtube import (
    ORIGINS as YoutubeOrigins,
    YoutubeTrackProvided,
)
from backend.src.track.domain.provided import TrackProvided, ProviderName, TrackUrl


INTERFACES_FOR_IMPLS: dict[Type[TrackProvided], Any] = {
    YoutubeTrackProvided: YoutubeAPIInterface,
}

PROVIDERS = {
    ProviderName("Youtube"): YoutubeTrackProvided,
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
    def _match_provider(domain: str) -> tuple[
        ProviderName,
        Type[TrackProvided],
    ]:
        if domain in YoutubeOrigins:
            provider_name = ProviderName("Youtube")
            return (provider_name, PROVIDERS[provider_name])
        else:
            raise TrackIdentifierError(ErrorMessages.UNKNOWN_PROVIDER)

    @classmethod
    def build(cls, url: str):
        track_url = cls.normalize(url)
        netloc = cls._extract_netloc(track_url)
        provider_name, provider_class = cls._match_provider(netloc)
        # ZAMIENIĆ NA DEPENDENCY INJECTION
        default_provider_api_impl = INTERFACES_FOR_IMPLS[provider_class]

        api_impl = default_provider_api_impl
        return provider_class(track_url, api_impl)

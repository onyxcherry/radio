from typing import Any, Optional, Type
from urllib.parse import urlparse, unquote

from kink import di

from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.domain.errors import TrackIdentifierError
from track.domain.errors import ErrorMessages
from track.domain.providers.youtube import (
    ORIGINS as YoutubeOrigins,
    YoutubeTrackProvided,
)
from track.domain.provided import (
    TrackProvided,
    ProviderName,
    TrackProvidedIdentity,
    TrackUrl,
)


_TEMP_INTERFACES_FOR_IMPLS: dict[Type[TrackProvided], Any] = {
    YoutubeTrackProvided: YoutubeAPIInterface,
}

_PROVIDERS_NAMES_MAPPING: dict[ProviderName, type[TrackProvided]] = {
    "Youtube": YoutubeTrackProvided,
}


class NotKnownProviderError(RuntimeError):
    pass


def _get_provided_track_class(name: ProviderName) -> type[TrackProvided]:
    result = _PROVIDERS_NAMES_MAPPING.get(name)
    if result is None:
        raise NotKnownProviderError(f"Brak zmapowanego providera {name}")
    return result


def _get_api_impl(provider: Type[TrackProvided]):
    return di[provider]


class TrackBuilder:
    @staticmethod
    def normalize(url: str) -> str:
        if not isinstance(url, str):
            raise TypeError(f"Passed {type(url)} type, expected 'str'")

        url = unquote(url)
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    @staticmethod
    def _extract_netloc(url: str) -> str:
        parsed = urlparse(url)
        netloc = parsed.netloc.split("@")[-1].split(":")[0]
        return netloc

    @staticmethod
    def _match_provider(domain: str) -> Optional[ProviderName]:
        if domain in YoutubeOrigins:
            return "Youtube"
        else:
            return None

    @classmethod
    def from_url(cls, url: str):
        normalized_url = cls.normalize(url)
        netloc = cls._extract_netloc(normalized_url)
        provider_name = cls._match_provider(netloc)

        if provider_name is None:
            raise TrackIdentifierError(ErrorMessages.UNKNOWN_PROVIDER)

        track_url = TrackUrl(normalized_url)
        track_provided_cls = _get_provided_track_class(provider_name)

        api_impl = _get_api_impl(track_provided_cls)
        return track_provided_cls.from_url(track_url, api_impl)

    @staticmethod
    def build(identity: TrackProvidedIdentity):
        track_provided_cls = _get_provided_track_class(identity.provider)

        api_impl = _get_api_impl(track_provided_cls)
        return track_provided_cls(identity.identifier, api_impl)

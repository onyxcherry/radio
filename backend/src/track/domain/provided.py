from typing import Any, NamedTuple, NewType, Self
from abc import ABC, abstractmethod


Identifier = NewType("Identifier", str)
ProviderName = NewType("ProviderName", str)

TrackUrl = NewType("TrackUrl", str)

Seconds = NewType("Seconds", int)


class TrackProvidedIdentity(NamedTuple):
    identifier: Identifier
    provider: ProviderName


class TrackProvided(ABC):
    @abstractmethod
    def __init__(self, identifier: Identifier, api: Any) -> None:
        pass

    @property
    @abstractmethod
    def identity(self) -> TrackProvidedIdentity:
        pass

    @property
    @abstractmethod
    def identifier(self) -> Identifier:
        pass

    @property
    @abstractmethod
    def provider(self) -> ProviderName:
        pass

    @property
    @abstractmethod
    def url(self) -> TrackUrl:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def duration(self) -> Seconds:
        pass

    @classmethod
    @abstractmethod
    def from_url(cls, url: TrackUrl, api: Any) -> Self:
        pass

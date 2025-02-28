from abc import ABC, abstractmethod
from typing import Any, Literal, NewType, Self

from pydantic.dataclasses import dataclass

Identifier = NewType("Identifier", str)
ProviderName = Literal["file", "Youtube"]

TrackUrl = NewType("TrackUrl", str)

Seconds = NewType("Seconds", int)


@dataclass(frozen=True, order=True)
class TrackProvidedIdentity:
    identifier: Identifier
    provider: ProviderName

    def __repr__(self):
        return f"TrackProvidedIdentity(identifier=Identifier({self.identifier!r}), provider={self.provider!r})"


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

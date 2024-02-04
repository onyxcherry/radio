from typing import NamedTuple, NewType
from abc import ABC, abstractmethod


TrackId = NewType("TrackId", str)
TrackUrl = NewType("TrackUrl", str)

Seconds = NewType("Seconds", int)


class IdWithProvider(NamedTuple):
    id: str
    provider: str


class TrackProvider(ABC):
    @property
    @abstractmethod
    def identity(self) -> TrackId:
        pass

    @property
    @abstractmethod
    def provider(self) -> str:
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

    @abstractmethod
    async def fetch_all_properties(self) -> None:
        pass

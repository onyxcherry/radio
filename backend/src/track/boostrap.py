from kink import di
from track.application.requests_service import RequestsService
from track.domain.library_repository import LibraryRepository
from track.domain.playlist_repository import PlaylistRepository

from track.infrastructure.inmemory_library_repository import (
    InMemoryLibraryRepository,
)
from track.infrastructure.inmemory_playlist_repository import (
    InMemoryPlaylistRepository,
)


def boostrap_di() -> None:
    di[LibraryRepository] = InMemoryLibraryRepository
    di[PlaylistRepository] = InMemoryPlaylistRepository
    di[RequestsService] = RequestsService(
        InMemoryLibraryRepository(), InMemoryPlaylistRepository()
    )

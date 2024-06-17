from kink import di
from building_blocks.clock import Clock, SystemClock
from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.infrastructure.youtube_api import YoutubeAPI
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
        InMemoryLibraryRepository(),
        InMemoryPlaylistRepository(),
        SystemClock(),
    )
    di[YoutubeAPIInterface] = YoutubeAPI
    di[Clock] = SystemClock()

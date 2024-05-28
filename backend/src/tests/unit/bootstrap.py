from kink import di
from track.domain.providers.youtube import YoutubeTrackProvider
from building_blocks.clock import Clock, SystemClock
from track.application.requests_service import RequestsService
from track.domain.library_repository import LibraryRepository
from track.domain.playlist_repository import PlaylistRepository
from track.infrastructure.inmemory_library_repository import (
    InMemoryLibraryRepository,
)
from track.infrastructure.inmemory_playlist_repository import (
    InMemoryPlaylistRepository,
)
from tests.inmemory_youtube_api import InMemoryYoutubeAPI
from track.application.interfaces.youtube_api import YoutubeAPIInterface


def boostrap_di() -> None:
    di[LibraryRepository] = InMemoryLibraryRepository
    di[PlaylistRepository] = InMemoryPlaylistRepository
    di[RequestsService] = RequestsService(
        InMemoryLibraryRepository(), InMemoryPlaylistRepository(), SystemClock()
    )
    di[YoutubeAPIInterface] = InMemoryYoutubeAPI()
    di[YoutubeTrackProvider] = InMemoryYoutubeAPI
    di[Clock] = SystemClock()


boostrap_di()

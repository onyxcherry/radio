from kink import di
from track.domain.library_repository import LibraryRepository
from track.infrastructure.db_library_repository import DBLibraryRepository
from track.infrastructure.db_playlist_repository import DBPlaylistRepository
from track.application.playlist import Playlist
from track.application.library import Library
from track.domain.providers.youtube import YoutubeTrackProvided
from building_blocks.clock import Clock, SystemClock
from track.application.requests_service import RequestsService
from track.infrastructure.inmemory_library_repository import (
    InMemoryLibraryRepository,
)
from track.infrastructure.inmemory_playlist_repository import (
    InMemoryPlaylistRepository,
)
from tests.inmemory_youtube_api import InMemoryYoutubeAPI
from track.application.interfaces.youtube_api import YoutubeAPIInterface


def bootstrap_di() -> None:
    # inmemory_library_repo = InMemoryLibraryRepository()
    # inmemory_playlist_repo = InMemoryPlaylistRepository()
    real_library_repo = DBLibraryRepository()
    real_playlist_repo = DBPlaylistRepository()
    system_clock = SystemClock()
    di[LibraryRepository] = real_library_repo
    di[RequestsService] = RequestsService(
        # inmemory_library_repo,
        # inmemory_playlist_repo,
        real_library_repo,
        real_playlist_repo,
        system_clock,
    )
    # di[Library] = Library(inmemory_library_repo)
    # di[Playlist] = Playlist(inmemory_playlist_repo)
    di[Library] = Library(real_library_repo)
    di[Playlist] = Playlist(real_playlist_repo)
    di[YoutubeAPIInterface] = InMemoryYoutubeAPI()
    di[YoutubeTrackProvided] = InMemoryYoutubeAPI
    di[Clock] = system_clock

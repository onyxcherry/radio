from kink import di
from track.application.library import Library
from track.application.playlist import Playlist
from track.domain.providers.youtube import YoutubeTrackProvided
from track.infrastructure.db_library_repository import DBLibraryRepository
from track.infrastructure.db_playlist_repository import DBPlaylistRepository
from building_blocks.clock import Clock, SystemClock
from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.infrastructure.youtube_api import YoutubeAPI
from track.application.requests_service import RequestsService


def boostrap_di() -> None:
    real_library_repo = DBLibraryRepository()
    real_playlist_repo = DBPlaylistRepository()
    system_clock = SystemClock()
    di[RequestsService] = RequestsService(
        real_library_repo,
        real_playlist_repo,
        system_clock,
    )
    di[Library] = Library(real_library_repo)
    di[Playlist] = Playlist(real_playlist_repo)
    di[YoutubeAPIInterface] = YoutubeAPI()
    di[YoutubeTrackProvided] = YoutubeAPI
    di[Clock] = system_clock

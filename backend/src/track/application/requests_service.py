from datetime import datetime

from kink import inject
from track.domain.breaks import Breaks
from track.application.dto import NewTrack, TrackRequestedAt
from track.application.library import Library
from track.builder import TrackBuilder
from track.domain.errors import PlayingTimeError
from track.application.playlist import Playlist
from track.domain.library_repository import LibraryRepository
from track.domain.playlist_repository import PlaylistRepository
from track.domain.status import Status


@inject
class RequestsService:
    def __init__(
        self, library_repo: LibraryRepository, playlist_repo: PlaylistRepository
    ):
        self._library = Library(library_repo)
        self._playlist = Playlist(playlist_repo)

    def request(self, requested: TrackRequestedAt):
        when_dt = Breaks.to_datetime(requested.when)
        n = datetime.utcnow()
        if when_dt < n:
            raise PlayingTimeError(
                f"Requested break time {when_dt} in the past, cannot add!"
            )
        if Breaks.is_weekday(requested.when):
            raise PlayingTimeError(
                f"Requested break time {when_dt} in a weekend, cannot add!"
            )

        track_status = self._library.get(requested.url)

        if track_status == Status.REJECTED:
            raise Exception("Utwór jest odrzucony, z czym do ludzi")
        elif track_status == Status.ACCEPTED:
            self._playlist.add_at(requested)
        elif track_status == Status.PENDING_APPROVAL:
            self._playlist.add_at(requested, waiting=True)

        elif track_status is None:
            track = TrackBuilder.build(requested.url)
            new_track = NewTrack(
                url=track.url, title=track.title, duration=track.duration
            )
            self._library.add(new_track)
            self._playlist.add_at(requested, waiting=True)

        else:
            raise NotImplementedError("Słabo generalnie")
        # co z waiting? Dodaj do waiting, gdy w bibliotece utwór czeka na akceptację (bo czekał bądź dopiero dodano do biblioteki)

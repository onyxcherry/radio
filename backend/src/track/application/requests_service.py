from kink import inject
from building_blocks.clock import Clock
from track.domain.breaks import PlayingTime
from track.application.dto import NewTrack, TrackRequestedAt
from track.application.library import Library
from track.builder import TrackBuilder
from track.domain.errors import PlayingTimeError, TrackDurationExceeded
from track.application.playlist import Playlist
from track.domain.library_repository import LibraryRepository
from track.domain.playlist_repository import PlaylistRepository
from track.domain.status import Status


@inject
class RequestsService:
    def __init__(
        self,
        library_repo: LibraryRepository,
        playlist_repo: PlaylistRepository,
        clock: Clock,
    ):
        self._library = Library(library_repo)
        self._playlist = Playlist(playlist_repo)
        self._clock = clock

    def _requested_playing_time_passed(self, requested_time: PlayingTime) -> bool:
        now = self._clock.now()
        requested_dt = requested_time.to_datetime()
        if now < requested_dt:
            return False
        return True

    def request(self, requested: TrackRequestedAt):
        if self._requested_playing_time_passed(requested.when):
            raise PlayingTimeError(
                f"Requested break time {requested.when} in the past, cannot add!"
            )
        if requested.when.is_weekday():
            raise PlayingTimeError(
                f"Requested break time {requested.when} in a weekend, cannot add!"
            )

        track_status = self._library.get(requested.url)

        if track_status == Status.REJECTED:
            raise Exception("Utwór jest odrzucony, z czym do ludzi")
        elif track_status == Status.ACCEPTED:
            self._playlist.add_at(requested, waiting=False)
        elif track_status == Status.PENDING_APPROVAL:
            self._playlist.add_at(requested, waiting=True)

        elif track_status is None:
            track = TrackBuilder.build(requested.url)
            new_track = NewTrack(
                url=track.url, title=track.title, duration=track.duration
            )
            try:
                self._library.add(new_track)
            except TrackDurationExceeded as ex:
                raise ValueError from ex
            try:
                self._playlist.add_at(requested, waiting=True)
            except PlayingTimeError as ex:
                raise ValueError from ex

        else:
            raise NotImplementedError("Słabo generalnie")
        # co z waiting? Dodaj do waiting, gdy w bibliotece utwór czeka na akceptację (bo czekał bądź dopiero dodano do biblioteki)

from dataclasses import dataclass
from typing import NewType, Optional
from kink import inject
from track.domain.entities import NewTrack, Status, TrackRequested
from building_blocks.clock import Clock
from track.domain.breaks import Breaks, PlayingTime, get_breaks_durations
from track.application.library import Library
from track.builder import TrackBuilder
from track.domain.errors import PlayingTimeError, TrackDurationExceeded
from track.application.playlist import Playlist
from track.domain.library_repository import LibraryRepository
from track.domain.playlist_repository import PlaylistRepository
from track.domain.provided import Seconds, TrackProvidedIdentity


MIN_TRACK_DURATION_SECONDS = Seconds(20)
MAX_TRACK_DURATION_SECONDS = Seconds(1200)


MINIMUM_PLAYING_TIME = Seconds(15)
MAX_TRACKS_QUEUED_ONE_BREAK = 8


Errors = NewType("Errors", list)


@dataclass(frozen=True)
class AddToLibraryStatus:
    added: bool
    waits_on_decision: bool


@dataclass(frozen=True)
class RequestResult:
    success: bool
    errors: Optional[Errors]


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

    @staticmethod
    def _check_valid_duration(duration: Seconds) -> bool:
        lower_limit = MIN_TRACK_DURATION_SECONDS
        upper_limit = MAX_TRACK_DURATION_SECONDS
        return lower_limit <= duration <= upper_limit

    def _requested_playing_time_passed(self, requested_time: PlayingTime) -> bool:
        now = self._clock.now()
        requested_dt = requested_time.to_datetime()
        if now < requested_dt:
            return False
        return True

    def _calc_left_time_on_break(self, duration: Seconds, break_: Breaks) -> Seconds:
        margin = Seconds(15)
        break_duration = get_breaks_durations()[break_]
        return Seconds(break_duration - duration - margin)

    def can_add_to_playlist(self, req: TrackRequested) -> Optional[Errors]:
        errors = list()

        if self._requested_playing_time_passed(req.when):
            errors.append(
                PlayingTimeError(
                    f"Requested break time {req.when} in the past, cannot add!"
                )
            )
        if req.when.is_on_weekend():
            errors.append(
                PlayingTimeError(
                    f"Requested break time {req.when} in a weekend, cannot add!"
                )
            )

        if self._playlist.check_played_or_queued_on_day(
            req.identity,
            req.when.date_,
        ):
            errors.append(PlayingTimeError("Już jest tego dnia"))

        # on_break_duration = self._playlist.get_tracks_duration_on_break(
        #     req.when, waiting=False
        # )
        # left_time = self._calc_left_time_on_break(
        #     on_break_duration,
        #     req.when.break_,
        # )
        # if left_time <= MINIMUM_PLAYING_TIME:
        # errors.append(PlayingTimeError("Not enough time to play"))

        tracks_on_break_count = self._playlist.get_tracks_count_on_break(
            req.when, waiting=False
        )
        if tracks_on_break_count >= MAX_TRACKS_QUEUED_ONE_BREAK:
            errors.append(PlayingTimeError("MAX_QUEUED_EXCEED"))
        if len(errors) > 0:
            return Errors(errors)
        return None

    def add_to_library(
        self, identity: TrackProvidedIdentity
    ) -> tuple[AddToLibraryStatus, Errors]:
        track_in_library = self._library.get(identity)
        track_status = track_in_library.status if track_in_library is not None else None

        if track_status == Status.REJECTED:
            return (
                AddToLibraryStatus(added=False, waits_on_decision=False),
                Errors(list()),
            )
        elif track_status == Status.ACCEPTED:
            return (
                AddToLibraryStatus(added=False, waits_on_decision=False),
                Errors(list()),
            )
        elif track_status == Status.PENDING_APPROVAL:
            return (
                AddToLibraryStatus(added=False, waits_on_decision=True),
                Errors(list()),
            )

        elif track_status is None:
            track = TrackBuilder.build(identity)
            identity = TrackProvidedIdentity(
                identifier=track.identifier, provider=track.provider
            )
            errors = list()
            if not self._check_valid_duration(track.duration):
                msg = f"Track duration must be between {MIN_TRACK_DURATION_SECONDS} and {MAX_TRACK_DURATION_SECONDS} seconds"
                errors.append(TrackDurationExceeded(msg))

            if len(errors) > 0:
                return (
                    AddToLibraryStatus(added=False, waits_on_decision=False),
                    Errors(errors),
                )

            new_track = NewTrack(
                identity=identity,
                url=track.url,
                title=track.title,
                duration=track.duration,
            )
            self._library.add(new_track)
            return (
                AddToLibraryStatus(added=True, waits_on_decision=True),
                Errors(list()),
            )

        else:
            raise NotImplementedError("Słabo generalnie")

    def request_on(
        self, identity: TrackProvidedIdentity, when: PlayingTime
    ) -> RequestResult:
        library_result, errors = self.add_to_library(identity)
        if errors is not None and len(errors) > 0:
            raise NotImplementedError("TODO: obsługa błędów")

        waits = library_result.waits_on_decision

        requested = TrackRequested(identity, when)
        errors = self.can_add_to_playlist(requested)
        if errors is None:
            self._playlist.add_at(requested, waits)
            return RequestResult(success=True, errors=None)
        else:
            return RequestResult(success=False, errors=errors)

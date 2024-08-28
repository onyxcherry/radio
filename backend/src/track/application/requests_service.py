from dataclasses import dataclass
import enum
from typing import Optional, Sequence
from kink import inject
from track.application.interfaces.events import EventsConsumer, EventsProducer
from track.domain.entities import NewTrack, Status, TrackInLibrary, TrackRequested
from building_blocks.clock import Clock
from track.domain.breaks import Breaks, PlayingTime, get_breaks_durations
from track.application.library import Library
from track.builder import TrackBuilder
from track.application.playlist import Playlist
from track.domain.library_repository import LibraryRepository
from track.domain.playlist_repository import PlaylistRepository
from track.domain.provided import Seconds, TrackProvidedIdentity


MIN_TRACK_DURATION_SECONDS = Seconds(20)
MAX_TRACK_DURATION_SECONDS = Seconds(1200)


MINIMUM_PLAYING_TIME = Seconds(15)
MAX_TRACKS_QUEUED_ONE_BREAK = 8


class LibraryTrackError(enum.StrEnum):
    INVALID_DURATION = enum.auto()
    TRACK_REJECTED = enum.auto()


class PlayingTimeError(enum.StrEnum):
    IN_THE_PAST = enum.auto()
    AT_THE_WEEKEND = enum.auto()
    ALREADY_ON_THIS_DAY = enum.auto()
    NOT_ENOUGH_TIME = enum.auto()
    MAX_COUNT_EXEEDED = enum.auto()


@dataclass(frozen=True)
class AddToLibraryStatus:
    added: bool
    waits_on_decision: bool
    errors: Optional[list[LibraryTrackError]] = None


@dataclass(frozen=True)
class RequestResult:
    success: bool
    errors: Optional[Sequence[LibraryTrackError | PlayingTimeError]] = None


@inject
class RequestsService:
    def __init__(
        self,
        library_repo: LibraryRepository,
        playlist_repo: PlaylistRepository,
        library_events_producer: EventsProducer,
        playlist_events_producer: EventsProducer,
        playlist_events_consumer: EventsConsumer,
        clock: Clock,
    ):
        self._clock = clock
        self._library = Library(library_repo, library_events_producer, clock)
        self._playlist = Playlist(
            playlist_repo, playlist_events_producer, playlist_events_consumer, clock
        )

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

    def can_add_to_playlist(
        self, req: TrackRequested
    ) -> Optional[list[PlayingTimeError]]:
        errors = list()

        if self._requested_playing_time_passed(req.when):
            errors.append(PlayingTimeError.IN_THE_PAST)

        if req.when.is_on_weekend():
            errors.append(PlayingTimeError.AT_THE_WEEKEND)

        if self._playlist.check_played_or_queued_on_day(
            req.identity,
            req.when.date_,
        ):
            errors.append(PlayingTimeError.ALREADY_ON_THIS_DAY)

        on_break_duration = self._playlist.get_tracks_duration_on_break(
            req.when, waiting=False
        )
        left_time = self._calc_left_time_on_break(
            on_break_duration,
            req.when.break_,
        )
        if left_time <= MINIMUM_PLAYING_TIME:
            errors.append(PlayingTimeError.NOT_ENOUGH_TIME)

        tracks_on_break_count = self._playlist.get_tracks_count_on_break(
            req.when, waiting=False
        )
        if tracks_on_break_count >= MAX_TRACKS_QUEUED_ONE_BREAK:
            errors.append(PlayingTimeError.MAX_COUNT_EXEEDED)

        if len(errors) > 0:
            return errors
        return None

    def add_to_library(self, identity: TrackProvidedIdentity) -> AddToLibraryStatus:
        track_in_library = self._library.get(identity)
        track_status = track_in_library.status if track_in_library is not None else None

        if track_status == Status.REJECTED:
            return AddToLibraryStatus(
                added=False,
                waits_on_decision=False,
                errors=[LibraryTrackError.TRACK_REJECTED],
            )

        elif track_status == Status.ACCEPTED:
            return AddToLibraryStatus(added=False, waits_on_decision=False)

        elif track_status == Status.PENDING_APPROVAL:
            return AddToLibraryStatus(added=False, waits_on_decision=True)

        elif track_status is None:
            track = TrackBuilder.build(identity)
            identity = TrackProvidedIdentity(
                identifier=track.identifier, provider=track.provider
            )

            errors = list()
            if not self._check_valid_duration(track.duration):
                errors.append(LibraryTrackError.INVALID_DURATION)

            if len(errors) > 0:
                return AddToLibraryStatus(
                    added=False, waits_on_decision=False, errors=errors
                )

            new_track = NewTrack(
                identity=identity,
                url=track.url,
                title=track.title,
                duration=track.duration,
            )
            self._library.add(new_track)
            return AddToLibraryStatus(added=True, waits_on_decision=True)

        else:
            raise NotImplementedError("Słabo generalnie")

    def request_on(
        self, identity: TrackProvidedIdentity, when: PlayingTime
    ) -> RequestResult:
        library_result = self.add_to_library(identity)
        if library_result.errors is not None and len(library_result.errors) > 0:
            return RequestResult(success=False, errors=library_result.errors)

        track = self._library.get(identity)
        if track is None:
            raise RuntimeError("Impossible")
        if track.duration is None:
            raise RuntimeError("TODO: handle nullable duration if needed")
        requested = TrackRequested(identity, when, track.duration)
        playlist_errors = self.can_add_to_playlist(requested)
        if playlist_errors is None:
            self._playlist.add(requested)
            return RequestResult(success=True, errors=None)
        else:
            return RequestResult(success=False, errors=playlist_errors)

    def accept(self, identity: TrackProvidedIdentity) -> TrackInLibrary:
        new_status = Status.ACCEPTED
        result = self._library._change_status(identity, new_status)
        return result.current

    def reject(self, identity: TrackProvidedIdentity) -> TrackInLibrary:
        new_status = Status.REJECTED
        result = self._library._change_status(identity, new_status)
        self._playlist.delete_all_by(identity)
        return result.current

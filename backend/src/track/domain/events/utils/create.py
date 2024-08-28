from datetime import date, datetime, timezone
from typing import Optional
from track.domain.events.library import (
    TrackAccepted,
    TrackAddedToLibrary,
    TrackRejected,
)
from track.domain.events.base import Event
from track.domain.breaks import PlayingTime
from track.domain.events.playlist import (
    TrackAddedToPlaylist,
    TrackDeletedFromPlaylist,
    TrackMarkedAsPlayed,
    TrackPlayed,
)
from track.domain.provided import Identifier, TrackProvidedIdentity


def _to_date(data: int) -> date:
    return date.fromordinal(data)


def _to_datetime(data: int | float) -> datetime:
    return datetime.fromtimestamp(data)


def _identity_from_dict(data: dict) -> Optional[TrackProvidedIdentity]:
    provider = data.get("provider")
    identifier = data.get("identifier")
    if provider is None or identifier is None:
        return None
    return TrackProvidedIdentity(identifier=Identifier(identifier), provider=provider)


def _playing_time_from_dict(data: Optional[dict]) -> Optional[PlayingTime]:
    if not isinstance(data, dict):
        return None
    date_ordinal = data.get("date")
    break_ = data.get("break")
    if date_ordinal is None or break_ is None:
        return None
    date_ = _to_date(date_ordinal)
    return PlayingTime(date_=date_, break_=break_)


def event_from_dict(data: dict) -> Event:
    if "event_name" not in data:
        raise RuntimeError("No event name in data!")
    if not isinstance(data.get("identity"), dict):
        raise RuntimeError('No "identity" in data!')
    if not "created":
        raise RuntimeError('No "created" in data!')

    if (identity := _identity_from_dict(data["identity"])) is None:
        raise RuntimeError('Bad "identity"!')

    # czy created musi być przekazywane do domeny aplikacyjnej?
    event_name = data["event_name"]
    created = datetime.fromtimestamp(data["created"] / 10**6, tz=timezone.utc)
    match event_name:
        case "TrackAddedToPlaylist":
            pt = _playing_time_from_dict(data.get("when"))
            if pt is None:
                raise RuntimeError("Bad data for playing time!")
            if (waits_on_approval := data.get("waits_on_approval")) is None:
                raise RuntimeError('No "waits_on_approval"!')
            return TrackAddedToPlaylist(
                identity=identity,
                when=pt,
                waits_on_approval=waits_on_approval,
                created=created,
            )
        case "TrackDeletedFromPlaylist":
            pt = _playing_time_from_dict(data.get("when"))
            if pt is None:
                raise RuntimeError("Bad data for playing time!")
            return TrackDeletedFromPlaylist(
                identity=identity,
                when=pt,
                created=created,
            )
        case "TrackPlayed":
            if (break_ := data.get("break")) is None:
                raise RuntimeError('No "break"!')
            if (start := data.get("start")) is None:
                raise RuntimeError('No "start"!')
            if (end := data.get("end")) is None:
                raise RuntimeError('No "end"!')
            start_dt = _to_datetime(start)
            end_dt = _to_datetime(end)
            return TrackPlayed(
                identity=identity,
                break_=break_,
                start=start_dt,
                end=end_dt,
                created=created,
            )
        case "TrackMarkedAsPlayed":
            pt = _playing_time_from_dict(data.get("when"))
            if pt is None:
                raise RuntimeError("Bad data for playing time!")
            return TrackMarkedAsPlayed(
                identity=identity,
                when=pt,
                created=created,
            )
        case "TrackAddedToLibrary":
            return TrackAddedToLibrary(
                identity=identity,
                created=created,
            )
        case "TrackAccepted":
            if (previous_status := data.get("previous_status")) is None:
                raise RuntimeError('No "previous_status"!')
            return TrackAccepted(
                identity=identity,
                previous_status=previous_status,
                created=created,
            )
        case "TrackRejected":
            if (previous_status := data.get("previous_status")) is None:
                raise RuntimeError('No "previous_status"!')
            return TrackRejected(
                identity=identity,
                previous_status=previous_status,
                created=created,
            )
        case _:
            raise RuntimeError(f'Unknown event "{event_name}"')

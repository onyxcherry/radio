from datetime import date
from track.domain.breaks import Breaks, PlayingTime
from track.domain.entities import NewTrack, Status, TrackInLibrary
from track.domain.provided import (
    Identifier,
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)


track1 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("a123"), provider="file"),
    title="A - B",
    url=TrackUrl("https://wisniewski.app/v=a123"),
    duration=Seconds(80),
)
track2 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("b456"), provider="file"),
    title="C - D",
    url=TrackUrl("https://wisniewski.app/v=a123"),
    duration=Seconds(210),
)
track3 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("c789"), provider="file"),
    title="E - F",
    url=TrackUrl("https://wisniewski.app/v=a123"),
    duration=Seconds(300),
)

yt_track1 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("ZDZiXmCl4pk"), provider="Youtube"),
    title="Kygo, Ava Max - Whatever",
    url=TrackUrl("https://www.youtube.com/watch?v=ZDZiXmCl4pk"),
    duration=Seconds(189),
)
yt_track2 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("8jrN6Kz2XbU"), provider="Youtube"),
    title="Lindsey Stirling + Otto Knows + Alex Aris - Dying For You",
    url=TrackUrl("https://www.youtube.com/watch?v=8jrN6Kz2XbU"),
    duration=Seconds(213),
)

NEW_TRACKS = [track1, track2, track3]

NEW_YT_TRACKS = [yt_track1, yt_track2]


IDENTITIES = [
    TrackProvidedIdentity(identifier=Identifier("ZDZiXmCl4pk"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("NBlSYkIJbIg"), provider="Youtube"),
]

TRACKS = [
    TrackInLibrary(
        identity=IDENTITIES[0],
        title="Kygo, Ava Max - Whatever",
        url=TrackUrl("https://www.youtube.com/watch?v=ZDZiXmCl4pk"),
        duration=Seconds(189),
        status=Status.ACCEPTED,
    ),
    TrackInLibrary(
        identity=IDENTITIES[1],
        title="Sokół - MC Hasselblad",
        url=TrackUrl("https://www.youtube.com/watch?v=NBlSYkIJbIg"),
        duration=Seconds(235),
        status=Status.PENDING_APPROVAL,
    ),
]

PASSED_PT = PlayingTime(
    break_=Breaks.FIRST,
    date_=date(2000, 1, 1),
)
FUTURE_PT = PlayingTime(
    break_=Breaks.FIRST,
    date_=date(2099, 1, 1),
)
FUTURE_PT_WEEKEND = PlayingTime(
    break_=Breaks.FIRST,
    date_=date(2099, 1, 3),
)

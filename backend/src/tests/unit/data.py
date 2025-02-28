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
    TrackProvidedIdentity(identifier=Identifier("2XNFzD08Zhc"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("6s70hLFEh2H"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("75JjzCrP4Ca"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("7xkKs41J3OG"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("9gvR9CAFMkU"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("CCp0cjFwTqn"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("DpLn2VgoOuD"), provider="Youtube"),
    TrackProvidedIdentity(identifier=Identifier("Nhxt5xkKAHT"), provider="Youtube"),
]

ACCEPTED_TRACKS = [
    TrackInLibrary(
        identity=IDENTITIES[0],
        title="Artist 1 - Track 1",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[0].identifier}"),
        duration=Seconds(189),
        status=Status.ACCEPTED,
    ),
    TrackInLibrary(
        identity=IDENTITIES[1],
        title="Artist 2 - Track 2",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[1].identifier}"),
        duration=Seconds(235),
        status=Status.ACCEPTED,
    ),
    TrackInLibrary(
        identity=IDENTITIES[2],
        title="Artist 3 - Track 3",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[2].identifier}"),
        duration=Seconds(181),
        status=Status.ACCEPTED,
    ),
]

PENDING_APPROVAL_TRACKS = [
    TrackInLibrary(
        identity=IDENTITIES[3],
        title="Artist 4 - Track 4",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[3].identifier}"),
        duration=Seconds(102),
        status=Status.PENDING_APPROVAL,
    ),
    TrackInLibrary(
        identity=IDENTITIES[4],
        title="Artist 5 - Track 5",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[4].identifier}"),
        duration=Seconds(142),
        status=Status.PENDING_APPROVAL,
    ),
    TrackInLibrary(
        identity=IDENTITIES[5],
        title="Artist 6 - Track 6",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[5].identifier}"),
        duration=Seconds(157),
        status=Status.PENDING_APPROVAL,
    ),
]

REJECTED_TRACKS = [
    TrackInLibrary(
        identity=IDENTITIES[6],
        title="Artist 7 - Track 7",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[6].identifier}"),
        duration=Seconds(189),
        status=Status.REJECTED,
    ),
    TrackInLibrary(
        identity=IDENTITIES[7],
        title="Artist 8 - Track 8",
        url=TrackUrl(f"https://www.youtube.com/watch?v={IDENTITIES[7].identifier}"),
        duration=Seconds(298),
        status=Status.REJECTED,
    ),
]

TRACKS = [*ACCEPTED_TRACKS, *PENDING_APPROVAL_TRACKS, *REJECTED_TRACKS]

PASSED_PT = PlayingTime(
    break_=Breaks.FIRST,
    date_=date(2000, 1, 3),
)
PASSED_PT_WEEKEND = PlayingTime(
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

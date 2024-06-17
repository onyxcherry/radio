from track.domain.entities import NewTrack
from track.domain.provided import (
    Identifier,
    ProviderName,
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)


track1 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("a123"), provider=ProviderName("file")),
    title="A - B",
    url=TrackUrl("https://wisniewski.app/v=a123"),
    duration=Seconds(80),
)
track2 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("b456"), provider=ProviderName("file")),
    title="C - D",
    url=TrackUrl("https://wisniewski.app/v=a123"),
    duration=Seconds(210),
)
track3 = NewTrack(
    TrackProvidedIdentity(identifier=Identifier("c789"), provider=ProviderName("file")),
    title="E - F",
    url=TrackUrl("https://wisniewski.app/v=a123"),
    duration=Seconds(300),
)

yt_track1 = NewTrack(
    TrackProvidedIdentity(
        identifier=Identifier("ZDZiXmCl4pk"), provider=ProviderName("Youtube")
    ),
    title="Kygo, Ava Max - Whatever",
    url=TrackUrl("https://www.youtube.com/watch?v=ZDZiXmCl4pk"),
    duration=Seconds(189),
)
yt_track2 = NewTrack(
    TrackProvidedIdentity(
        identifier=Identifier("8jrN6Kz2XbU"), provider=ProviderName("Youtube")
    ),
    title="Lindsey Stirling + Otto Knows + Alex Aris - Dying For You",
    url=TrackUrl("https://www.youtube.com/watch?v=8jrN6Kz2XbU"),
    duration=Seconds(213),
)

TRACKS = [track1, track2, track3]

YT_TRACKS = [yt_track1, yt_track2]

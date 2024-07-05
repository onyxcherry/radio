from track.domain.entities import Status, TrackInLibrary
from track.domain.provided import (
    Identifier,
    ProviderName,
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)


IDENTITIES = [
    TrackProvidedIdentity(
        identifier=Identifier("ZDZiXmCl4pk"), provider=ProviderName("youtube")
    ),
    TrackProvidedIdentity(
        identifier=Identifier("NBlSYkIJbIg"), provider=ProviderName("youtube")
    ),
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

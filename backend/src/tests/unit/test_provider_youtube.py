from typing import Final

import pytest

from tests.inmemory_youtube_api import InMemoryYoutubeAPI
from track.builder import TrackBuilder
from track.domain.errors import TrackIdentifierError
from track.domain.provided import TrackUrl
from track.domain.providers.youtube import YoutubeTrackProvided

expected: Final = "i-uYn_lp6Qg"

api = InMemoryYoutubeAPI()


@pytest.mark.parametrize(
    "track_url",
    [
        f"https://www.youtube.com/watch?v={expected}",
        f"www.youtube.com/watch?v={expected}",
        f"youtube.com/watch?v={expected}",
        f"https://youtu.be/{expected}",
        f"https://m.youtube.com/watch%3Fv%3D{expected}",
        (
            f"https://www.youtube.com/watch?v={expected}"
            + "&list=RDCMUCTEopVgqNCUhJq57CxTc4aw"
            + "&start_radio=1&rv=YZo9Am1t9qw&t=4"
        ),
    ],
)
def test_extracts_youtube_id(track_url):
    track_id = YoutubeTrackProvided.extract_id(track_url)
    assert track_id == expected


def test_raises_error_url_invalid():
    invalid_urls = [
        "pqrUQrAcfo4",
        "https://example.com/url=https://youtube.com/watch?v=i-uYn_lp6Qg",
    ]

    for track_url in invalid_urls:
        with pytest.raises(TrackIdentifierError):
            _ = TrackBuilder.from_url(track_url)


def test_gets_track_duration():
    url = TrackUrl("https://www.youtube.com/watch?v=YBcdt6DsLQA")
    youtube_track = YoutubeTrackProvided.from_url(url, api)

    assert youtube_track.duration == 147


def test_gets_track_title():
    url = TrackUrl("https://www.youtube.com/watch?v=YBcdt6DsLQA")
    youtube_track = YoutubeTrackProvided.from_url(url, api)

    assert youtube_track.title == "The Beatles - In My Life (Remastered 2009)"

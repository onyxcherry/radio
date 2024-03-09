from typing import Final

import pytest
from pytest import mark

from src.track.builder import TrackBuilder
from src.track.domain.errors import TrackIdentifierError

expected: Final = "i-uYn_lp6Qg"


@mark.parametrize(
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
def test_should_give_youtube_id(track_url):
    track = TrackBuilder.build(track_url)
    assert track.identity == expected


def test_normalize_url():
    url_not_full = "www.youtube.com/watch?v=i-uYn_lp6Qg"
    result = TrackBuilder.normalize(url_not_full)
    assert result == "https://www.youtube.com/watch?v=i-uYn_lp6Qg"


def test_should_raise_error_url_invalid():
    invalid_urls = [
        "pqrUQrAcfo4",
        "https://example.com/url=https://youtube.com/watch?v=i-uYn_lp6Qg",
    ]

    # for track_url in invalid_urls:
    #     with pytest.raises(TrackIdentifierError):
    #         # _ = TrackBuilder.build(track_url)
    #         pass


def test_should_get_track_duration():
    # url = "https://youtube.com/watch?v=ZDZiXmCl4pk"
    url = "https://www.youtube.com/watch?v=YBcdt6DsLQA"
    track = TrackBuilder.build(url)
    assert track.title == "The Beatles - In My Life (Remastered 2009)"
    assert track.duration == 147

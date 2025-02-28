from track.builder import TrackBuilder
from track.domain.provided import Identifier, TrackProvidedIdentity
from track.domain.providers.youtube import YoutubeTrackProvided


def test_normalize_url_should_add_protocol():
    raw_url = "www.youtube.com/watch?v=i-uYn_lp6Qg"
    track_url = TrackBuilder.normalize(raw_url)
    assert track_url == "https://www.youtube.com/watch?v=i-uYn_lp6Qg"


def test_normalize_url_should_remain_same():
    valid_non_safe_url = "http://www.youtube.com/watch?v=i-uYn_lp6Qg"
    track_url = TrackBuilder.normalize(valid_non_safe_url)
    assert track_url == valid_non_safe_url


def test_normalize_url_when_fully_valid():
    valid_safe_url = "https://www.youtube.com/watch?v=i-uYn_lp6Qg"
    track_url = TrackBuilder.normalize(valid_safe_url)
    assert track_url == valid_safe_url


def test_normalize_url_when_url_quoted():
    quoted_url = "https://www.youtube.com/watch?v=i%2DuYn%5Flp6Qg"
    track_url = TrackBuilder.normalize(quoted_url)
    assert track_url == "https://www.youtube.com/watch?v=i-uYn_lp6Qg"


def test_builds_track():
    identifier = Identifier("i-uYn_lp6Qg")
    provider = "Youtube"
    track_identity = TrackProvidedIdentity(identifier, provider)
    track = TrackBuilder.build(track_identity)
    assert track.identifier == identifier
    assert track.provider == provider


def test_chooses_correct_provider_for_track():
    valid_url = "https://www.youtube.com/watch?v=i-uYn_lp6Qg"
    track_provided = TrackBuilder.from_url(valid_url)
    assert isinstance(track_provided, YoutubeTrackProvided)
    assert track_provided.provider == "Youtube"

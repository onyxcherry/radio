from src.track.builder import TrackBuilder


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

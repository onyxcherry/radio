from src.track.domain.duration import parse_isoduration


def test_parse_isoduration_seconds():
    assert parse_isoduration("PT7S") == {
        "hours": 0,
        "minutes": 0,
        "seconds": 7,
    }


def test_parse_isoduration_minutes_seconds():
    assert parse_isoduration("PT3M16S") == {
        "hours": 0,
        "minutes": 3,
        "seconds": 16,
    }


def test_parse_isoduration_full():
    assert parse_isoduration("PT15H23M42S") == {
        "hours": 15,
        "minutes": 23,
        "seconds": 42,
    }

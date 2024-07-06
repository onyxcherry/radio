from datetime import date
from src.track.domain.breaks import (
    Breaks,
    PlayingTime,
    get_breaks_starting_times,
)


def test_playing_time_converts_to_datetime():
    d = date(2024, 5, 28)
    b = Breaks.THIRD
    pt = PlayingTime(date_=d, break_=b)
    assert pt.to_datetime().time() == get_breaks_starting_times()[2]

from datetime import date
from src.track.domain.breaks import BREAKS_START_TIMES, Breaks, PlayingTime


def test_playing_time_converts_to_datetime():
    d = date(2024, 5, 28)
    b = Breaks.THIRD
    pt = PlayingTime(date_=d, break_=b)
    assert pt.to_datetime().time() == list(BREAKS_START_TIMES.keys())[2]

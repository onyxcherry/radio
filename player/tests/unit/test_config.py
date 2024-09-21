from datetime import time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import RootModel
from player.src.config import (
    BreaksConfig,
    BreakData,
    load_config_from_yaml,
)
from player.src.domain.types import Seconds


def test_parses_start_time():
    first = BreakData.from_dict({"start": "08:30", "end": "08:40"})
    second = BreakData.from_dict({"start": "08:30", "duration": 600})

    artificial = BreakData(start=time(8, 30), duration=Seconds(600), end=time(8, 40))
    assert first == second
    assert first == artificial
    assert (
        artificial
        == BreakData(start=time(8, 30), duration=Seconds(600))
        == BreakData(start=time(8, 30), end=time(8, 40))
    )

    first_dumped = RootModel[BreakData](first).model_dump()
    second_dumped = RootModel[BreakData](second).model_dump()
    assert first_dumped == second_dumped
    assert first_dumped == {"start": time(8, 30), "duration": 600}


def test_loads_config():
    config_path = Path(__file__).parent.parent / "data" / "test-config.yaml"
    result = load_config_from_yaml(config_path=config_path)
    assert result == {
        "breaks": {
            "offset": {"seconds": 17},
            "timezone": "Europe/Warsaw",
            "list": [
                {"start": "08:30", "end": "08:40"},
                {"start": "09:25", "end": "09:35"},
                {"start": "10:20", "end": "10:30"},
                {"start": "11:15", "end": "11:30"},
                {"start": "12:15", "end": "12:25"},
                {"start": "13:10", "end": "13:20"},
                {"start": "14:05", "end": "14:15"},
                {"start": "15:00", "end": "15:10"},
            ],
        }
    }

    bc = BreaksConfig.from_dict(result["breaks"])
    assert bc == BreaksConfig(
        offset=timedelta(seconds=17),
        timezone=ZoneInfo(key="Europe/Warsaw"),
        breaks=[
            BreakData(start=time(8, 30), duration=Seconds(600), end=time(8, 40)),
            BreakData(start=time(9, 25), duration=Seconds(600), end=time(9, 35)),
            BreakData(start=time(10, 20), duration=Seconds(600), end=time(10, 30)),
            BreakData(start=time(11, 15), duration=Seconds(900), end=time(11, 30)),
            BreakData(start=time(12, 15), duration=Seconds(600), end=time(12, 25)),
            BreakData(start=time(13, 10), duration=Seconds(600), end=time(13, 20)),
            BreakData(start=time(14, 5), duration=Seconds(600), end=time(14, 15)),
            BreakData(start=time(15, 0), duration=Seconds(600), end=time(15, 10)),
        ],
    )

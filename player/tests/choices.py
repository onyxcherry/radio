from dataclasses import dataclass
from datetime import time, timedelta
from zoneinfo import ZoneInfo

from player.src.config import BreaksConfig
from player.src.domain.types import Seconds

breaks_config = BreaksConfig(
    start_times={
        time(8, 30): Seconds(10 * 60),
        time(9, 25): Seconds(10 * 60),
        time(10, 20): Seconds(10 * 60),
        time(11, 15): Seconds(15 * 60),
        time(12, 15): Seconds(10 * 60),
        time(13, 10): Seconds(10 * 60),
        time(14, 5): Seconds(10 * 60),
        time(15, 00): Seconds(10 * 60),
    },
    offset=timedelta(seconds=17),
    timezone=ZoneInfo("Europe/Warsaw"),
)


@dataclass
class DIChoices:
    real_db: bool
    real_msg_broker: bool

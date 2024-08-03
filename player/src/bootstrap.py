from datetime import datetime
from zoneinfo import ZoneInfo
from kink import di


from player.src.building_blocks.clock import Clock, FixedClock
from player.src.domain.interfaces.player import Player
from player.src.infrastructure.madeup_player import MadeupPlayer


def bootstrap_di():
    _breaks_timezone = ZoneInfo("Europe/Warsaw")
    dt = datetime(2024, 8, 1, 8, 34, 11, tzinfo=_breaks_timezone)
    clock = FixedClock(dt)
    di[Clock] = clock
    di[Player] = MadeupPlayer()

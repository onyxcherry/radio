from typing import Optional
from kink import inject
from player.src.application.break_observer import BreakObserver
from player.src.application.playing_observer import PlayingObserver
from player.src.domain.entities import ScheduledTrack


@inject
class PlayerStatus:
    def __init__(
        self, playing_observer: PlayingObserver, break_observer: BreakObserver
    ) -> None:
        self._playing_observer = playing_observer
        self._break_observer = break_observer

    @property
    def track_is_playing(self) -> bool:
        return self._playing_observer.track_is_playing

    @property
    def track_playing(self) -> Optional[ScheduledTrack]:
        return self._playing_observer.track_playing

    @property
    def during_break(self) -> bool:
        return self._break_observer.current is not None

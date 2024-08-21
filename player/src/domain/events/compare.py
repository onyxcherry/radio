from dataclasses import asdict, dataclass, is_dataclass
from typing import TypeGuard, TypeVar


Ev = TypeVar("Ev")


def events_differ_only_last_changed(event1: Ev, event2: Ev) -> bool:
    if not is_dataclass(event1) or not is_dataclass(event2):
        raise RuntimeError("At least one obj not being dataclass")
    first = asdict(event1)
    first.pop("last_changed")
    second = asdict(event2)
    second.pop("last_changed")
    return first == second

from typing import Literal, NewType


Identifier = NewType("Identifier", str)
ProviderName = Literal["file", "Youtube"]

Seconds = NewType("Seconds", int)

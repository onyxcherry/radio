from track.domain.events.base import Event


class InMemoryEvents:
    def __init__(self) -> None:
        self._messages = {}

    def get_for(self, topic: str) -> list[Event]:
        return self._messages.get(topic) or list()

    def get_and_ack_for(self, topic: str, count: int) -> list[Event]:
        if topic in self._messages:
            messages = self._messages[topic]
            acked, rest = messages[:count], messages[count:]
            self._messages[topic] = rest
            return acked
        return list()

    def append(self, message: Event, topic: str) -> None:
        if topic not in self._messages:
            self._messages[topic] = []
        self._messages[topic].append(message)

    def reset(self) -> None:
        self._messages = {}

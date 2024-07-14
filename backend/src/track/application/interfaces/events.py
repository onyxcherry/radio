from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Callable, Optional

from track.infrastructure.messaging.schema_utils import SchemaRegistryConfig
from track.domain.events.base import Event


@dataclass(frozen=True)
class ConsumerConnectionOptions:
    bootstrap_servers: str
    client_id: str
    group_id: Optional[str]


@dataclass(frozen=True)
class ProducerConnectionOptions:
    bootstrap_servers: str
    client_id: str


@dataclass(frozen=True)
class MessagesOptions:
    partitioner: Optional[Callable] = None
    key_serializer: Optional[Callable] = None
    value_serializer: Optional[Callable] = None


class EventsConsumer(ABC):
    @abstractmethod
    def __init__(
        self,
        conn_options: ConsumerConnectionOptions,
        msg_options: MessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def subscribe(
        self, topics: str | list[str], pattern: Optional[re.Pattern] = None
    ) -> None:
        pass

    @abstractmethod
    def consume(self, limit: int) -> Event:
        pass


class EventsProducer(ABC):
    @abstractmethod
    def __init__(
        self,
        conn_options: ProducerConnectionOptions,
        msg_options: MessagesOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def produce(self, topic: str, message: Event) -> None:
        pass

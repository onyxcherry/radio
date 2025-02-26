from abc import ABC, abstractmethod
from pydantic.dataclasses import dataclass
import re
from typing import Callable, Optional

from track.infrastructure.messaging.schema_utils import SchemaRegistryConfig
from track.domain.events.base import Event


@dataclass(frozen=True)
class ConsumerConnectionOptions:
    bootstrap_servers: str
    client_id: str
    group_id: str


@dataclass(frozen=True)
class ProducerConnectionOptions:
    bootstrap_servers: str
    client_id: str


@dataclass(frozen=True)
class ConsumerMessagesOptions:
    value_deserializer: Callable
    key_deserializer: Optional[Callable] = None


@dataclass(frozen=True)
class ProducerMessagesOptions:
    value_serializer: Callable
    key_serializer: Callable
    partitioner: Optional[Callable] = None


class EventsConsumer(ABC):
    @abstractmethod
    def __init__(
        self,
        conn_options: ConsumerConnectionOptions,
        msg_options: ConsumerConnectionOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def subscribe(self, topic: str | list[str]) -> None:
        pass

    @abstractmethod
    def consume(self, limit: int) -> list[Event]:
        pass


class EventsProducer(ABC):
    @abstractmethod
    def __init__(
        self,
        conn_options: ProducerConnectionOptions,
        msg_options: ProducerConnectionOptions,
        schema_config: SchemaRegistryConfig,
        test: bool = False,
    ) -> None:
        pass

    @abstractmethod
    def produce(self, message: Event) -> None:
        pass

from player.src.infrastructure.messaging.inmemory_events_consumer import (
    InMemoryEventsConsumer,
)
from player.src.infrastructure.messaging.inmemory_events_producer import (
    InMemoryEventsProducer,
)
from player.src.application.interfaces.events import EventsConsumer, EventsProducer


def sync_messages_from_producer_to_consumer(
    producer: EventsProducer, consumer: EventsConsumer, *, real_msg_broker: bool
):
    if (
        not real_msg_broker
        and isinstance(consumer, InMemoryEventsConsumer)
        and isinstance(producer, InMemoryEventsProducer)
    ):
        consumer._messages = producer._messages
        producer._messages = {}

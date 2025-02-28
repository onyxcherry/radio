from confluent_kafka import Consumer, KafkaException, TopicPartition
from confluent_kafka.admin import AdminClient
from kink import di

from config import Settings, get_logger
from tests.choices import DIChoices
from track.infrastructure.messaging.inmemory_events_helper import InMemoryEvents

logger = get_logger(__name__)


def reset_offset(topic: str) -> None:
    settings = di[Settings]
    conf = {
        "bootstrap.servers": settings.broker_bootstrap_server,
    }
    consumer = Consumer({"group.id": "tests-1", **conf})
    tp = TopicPartition(topic, 0)
    low_watermark, high_watermark = consumer.get_watermark_offsets(tp)
    if low_watermark == high_watermark:
        return
    tp2 = TopicPartition(topic, 0, high_watermark)

    a = AdminClient(conf)
    futmap = a.delete_records([tp2])
    partition, fut = list(futmap.items())[0]
    try:
        fut.result()
    except KafkaException as ex:
        logger.error(f"Exception raised for partition: {partition}")
        logger.exception(ex)


def reset_events() -> None:
    di_choices = di[DIChoices]
    if di_choices.real_msg_broker:
        topics = ["queue", "library"]
        for topic in topics:
            reset_offset(topic)
    else:
        di[InMemoryEvents].reset()

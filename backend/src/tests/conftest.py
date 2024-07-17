import pytest

from track.application.interfaces.events import EventsConsumer, EventsProducer


def pytest_addoption(parser):
    parser.addoption(
        "--realdb", action="store_true", default=False, help="run tests with real db"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "realdb: mark test which needs real db")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--realdb"):
        return
    skip_realdb = pytest.mark.skip(reason="need --realdb option to run")
    for item in items:
        if "realdb" in item.keywords:
            item.add_marker(skip_realdb)


def sync_messages_from_producer_to_consumer(
    producer: EventsProducer, consumer: EventsConsumer
):
    UNIT = True
    if UNIT:
        consumer._messages = producer._messages

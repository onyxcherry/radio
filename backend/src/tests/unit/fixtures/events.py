import subprocess
from typing import Optional, Sequence

from pytest import fixture
from track.infrastructure.messaging.inmemory_events_consumer import (
    InMemoryEventsConsumer,
)
from track.infrastructure.messaging.inmemory_events_producer import (
    InMemoryEventsProducer,
)


@fixture(scope="session")
def provide_config(request) -> bool:
    is_realmsgbroker = request.config.getoption("realmsgbroker")
    return is_realmsgbroker


def reset_events(
    realmsgbroker: bool,
    events_producers_consumers: Optional[
        Sequence[InMemoryEventsProducer | InMemoryEventsConsumer]
    ],
) -> None:
    if realmsgbroker:
        command = "/home/tomasz/.local/bin/rpk -X brokers=127.0.0.1:19092 topic trim-prefix queue -o end --no-confirm"
        result = subprocess.run(
            command, shell=True, check=False, text=True, capture_output=True
        )
        # ./kafka-delete-records.sh --bootstrap-server localhost:19092 --offset-json-file ~/delete-records.json
        # {"partitions": [{"topic": "queue", "partition": 0, "offset": 1}], "version": 1}
    else:
        for events_handler in events_producers_consumers or []:
            if isinstance(events_handler, InMemoryEventsProducer):
                events_handler.reset()
            elif isinstance(events_handler, InMemoryEventsProducer):
                events_handler.reset()

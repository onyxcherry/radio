import subprocess
from kink import di
from player.src.infrastructure.messaging.inmemory_events_helper import InMemoryEvents
from player.tests.choices import DIChoices


def reset_events() -> None:
    di_choices = di[DIChoices]
    if di_choices.real_msg_broker:
        command = "/home/tomasz/.local/bin/rpk -X brokers=127.0.0.1:19092 topic trim-prefix queue -o end --no-confirm"
        result = subprocess.run(
            command, shell=True, check=False, text=True, capture_output=True
        )
        # ./kafka-delete-records.sh --bootstrap-server localhost:19092 --offset-json-file ~/delete-records.json
        # {"partitions": [{"topic": "queue", "partition": 0, "offset": 1}], "version": 1}
    else:
        di[InMemoryEvents].reset()

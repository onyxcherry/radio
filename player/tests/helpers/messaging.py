import json
import subprocess
import tempfile
from kink import di
from player.src.infrastructure.messaging.inmemory_events_helper import InMemoryEvents
from player.tests.choices import DIChoices


def reset_events() -> None:
    di_choices = di[DIChoices]
    if di_choices.real_msg_broker:
        data = {
            "partitions": [{"topic": "queue", "partition": 0, "offset": 58881}],
            "version": 1,
        }
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete_on_close=False
        ) as fp:
            json.dump(data, fp)
            fp.close()
            command = f"/home/tomasz/kafka_2.13-3.7.1/bin/kafka-run-class.sh org.apache.kafka.tools.DeleteRecordsCommand --bootstrap-server localhost:19092 --offset-json-file {fp.name}"
            result = subprocess.run(
                command, shell=True, check=False, text=True, capture_output=True
            )
    else:
        di[InMemoryEvents].reset()

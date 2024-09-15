import json
import subprocess
import tempfile
from kink import di
from track.infrastructure.messaging.inmemory_events_helper import InMemoryEvents
from tests.choices import DIChoices


def reset_offset(topic: str) -> None:
    kafka_run_class_sh_path = "/home/tomasz/kafka_2.13-3.7.1/bin/kafka-run-class.sh"
    bootstrap_server = "localhost:19092"
    get_offset_command = f"{kafka_run_class_sh_path} org.apache.kafka.tools.GetOffsetShell --bootstrap-server {bootstrap_server} --topic {topic}"
    get_offset_result = subprocess.run(
        get_offset_command, shell=True, check=True, text=True, capture_output=True
    )
    got_offset = int(get_offset_result.stdout.split(":")[-1])

    data = {
        "partitions": [{"topic": topic, "partition": 0, "offset": got_offset}],
        "version": 1,
    }
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".json", delete_on_close=False
    ) as fp:
        delete_command = f"{kafka_run_class_sh_path} org.apache.kafka.tools.DeleteRecordsCommand --bootstrap-server {bootstrap_server} --offset-json-file {fp.name}"
        json.dump(data, fp)
        fp.close()
        delete_result = subprocess.run(
            delete_command, shell=True, check=False, text=True, capture_output=True
        )
        # TODO:
        # assert "OffsetOutOfRangeException" not in delete_result.stdout


def reset_events() -> None:
    di_choices = di[DIChoices]
    if di_choices.real_msg_broker:
        topics = ["queue", "library"]
        for topic in topics:
            reset_offset(topic)
    else:
        di[InMemoryEvents].reset()

import json
from urllib.parse import urljoin

import requests
from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from kink import di

from boostrap import bootstrap_config
from config import Settings
from track.infrastructure.messaging.schema_utils import merge_sub_schemas
from track.infrastructure.persistence import dbinit

topics_to_register = ["library-value", "queue-value"]


def main():
    bootstrap_config()
    settings = di[Settings]

    dbinit.main()
    schema_reg_subjects_url = urljoin(settings.schema_registry_url, "/subjects")
    try:
        registered_schemas = requests.get(
            schema_reg_subjects_url, timeout=(2, 3)
        ).json()
    except (requests.ConnectionError, requests.Timeout) as ex:
        print("Cannot connect to schema registry, exiting now...")
        raise ex
    for topic in topics_to_register:
        if topic not in registered_schemas:
            schema = merge_sub_schemas(topic.split("-")[0])
            data = json.dumps({"schema": json.dumps(schema)})
            response = requests.post(
                url=urljoin(
                    settings.schema_registry_url, f"/subjects/{topic}/versions"
                ),
                data=data,
                headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            ).json()
            print(f"{topic}: {response}")

    conf = {
        "bootstrap.servers": settings.broker_bootstrap_server,
    }
    a = AdminClient(conf)
    existing_topics = a.list_topics().topics
    library_topic = NewTopic("library", num_partitions=1)
    queue_topic = NewTopic("queue", num_partitions=1)
    if all(topic.topic in existing_topics for topic in [library_topic, queue_topic]):
        pass
    elif any(topic.topic in existing_topics for topic in [library_topic, queue_topic]):
        raise RuntimeWarning("Some topic exists in cluster but not all, exiting...")
    else:
        topics_creation_result = a.create_topics([library_topic, queue_topic])
        for topic_name, fut in topics_creation_result.items():
            try:
                fut.result()
            except KafkaException as ex:
                print(f"Error occured during creating topic: {topic_name}")
                print(ex)
                return

    print("Initialized backend successfully")


if __name__ == "__main__":
    main()

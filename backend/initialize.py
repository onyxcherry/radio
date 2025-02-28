import json
from urllib.parse import urljoin

import requests
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


if __name__ == "__main__":
    main()
    print("Initialized backend successfully")

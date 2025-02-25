from config import Config
from track.infrastructure.messaging.schema_utils import merge_sub_schemas
from track.infrastructure.persistence import dbinit
import requests
from urllib.parse import urljoin
import json

schema_reg_host = "http://redpanda-0:8081"
topics_to_register = ["library-value", "queue-value"]


def main():
    dbinit.main()
    schema_reg_subjects_url = urljoin(schema_reg_host, "/subjects")
    registered_schemas = requests.get(schema_reg_subjects_url, timeout=(2, 3)).json()
    for topic in topics_to_register:
        if topic not in registered_schemas:
            schema = merge_sub_schemas(topic.split("-")[0])
            data = json.dumps({"schema": json.dumps(schema)})
            response = requests.post(
                url=urljoin(schema_reg_host, f"/subjects/{topic}/versions"),
                data=data,
                headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            ).json()
            print(f"{topic}: {response}")


if __name__ == "__main__":
    main()

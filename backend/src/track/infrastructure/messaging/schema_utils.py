from dataclasses import dataclass
from typing import Literal, Optional
from confluent_kafka.schema_registry import SchemaRegistryClient


@dataclass
class SchemaRegistryConfig:
    url: str
    schema_id: int | Literal["latest"]
    subject_name: Optional[str]


def fetch_schema(config: SchemaRegistryConfig) -> tuple[SchemaRegistryClient, str]:
    schema_registry_conf = {"url": config.url}
    client = SchemaRegistryClient(schema_registry_conf)
    schema_id = config.schema_id
    subject_name = config.subject_name
    schema_str = None
    if schema_id == "latest" and subject_name is not None:
        schema = client.get_latest_version(subject_name)
        schema_str = schema.schema.schema_str
    elif isinstance(schema_id, int):
        schema = client.get_schema(schema_id)
        schema_str = schema.schema_str
    else:
        raise RuntimeError(f"Invalid schema_id: {schema_id}")
    return client, schema_str

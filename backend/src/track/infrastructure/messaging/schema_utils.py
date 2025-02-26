from pydantic.dataclasses import dataclass
import os
from typing import Literal, Optional
from confluent_kafka.schema_registry import SchemaRegistryClient
from fastavro.schema import load_schema
from fastavro.types import Schema


@dataclass
class SchemaRegistryConfig:
    url: str
    topic_name: str
    schema_id: int | Literal["latest"]
    subject_name: Optional[str] = None


def create_client(config: SchemaRegistryConfig) -> SchemaRegistryClient:
    schema_registry_conf = {"url": config.url}
    client = SchemaRegistryClient(schema_registry_conf)
    return client


def fetch_schema(
    client: SchemaRegistryClient,
    schema_id: int | Literal["latest"],
    subject_name: Optional[str],
) -> str:
    schema_str = None
    if schema_id == "latest" and subject_name is not None:
        schema = client.get_latest_version(subject_name)
        schema_str = schema.schema.schema_str
    elif isinstance(schema_id, int):
        schema = client.get_schema(schema_id)
        schema_str = schema.schema_str
    else:
        raise RuntimeError(f"Invalid schema_id: {schema_id}")
    return schema_str


def merge_sub_schemas(schema: Literal["queue", "library"]) -> Schema:
    dir_name = os.path.dirname(__file__)
    path = os.path.join(dir_name, "./schemas/", f"{schema}.avsc")
    abs_path = os.path.abspath(path)
    parsed_schema = load_schema(abs_path)
    return parsed_schema

from pathlib import Path

from confluent_kafka.serialization import StringSerializer
from kink import di

from building_blocks.clock import Clock, SystemClock
from config import Config, Settings, config_dict_to_class, load_config_from_yaml
from track.application.interfaces.events import (
    ConsumerConnectionOptions,
    ConsumerMessagesOptions,
    ProducerConnectionOptions,
    ProducerMessagesOptions,
)
from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.application.library import Library
from track.application.playlist import Playlist
from track.application.requests_service import RequestsService
from track.domain.events.recreate import parse_event
from track.domain.events.serialize import serialize_event
from track.domain.providers.youtube import YoutubeTrackProvided
from track.infrastructure.db_library_repository import DBLibraryRepository
from track.infrastructure.db_playlist_repository import DBPlaylistRepository
from track.infrastructure.messaging.kafka_events_consumer import KafkaAvroEventsConsumer
from track.infrastructure.messaging.kafka_events_producer import KafkaAvroEventsProducer
from track.infrastructure.messaging.schema_utils import SchemaRegistryConfig
from track.infrastructure.messaging.types import (
    LibraryEventsProducer,
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)
from track.infrastructure.youtube_api import YoutubeAPI

CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.yaml"
CONFIG_SCHEMA_PATH = Path(__file__).parent.parent / "config.schema.json"


def bootstrap_config() -> None:
    config_dict = load_config_from_yaml(
        config_path=CONFIG_FILE_PATH, schema_path=CONFIG_SCHEMA_PATH
    )
    settings = Settings()  # type: ignore
    config = config_dict_to_class(config_dict)
    di[Config] = config
    di[Settings] = settings


def boostrap_di() -> None:
    bootstrap_config()
    clock = SystemClock()
    config = di[Config]
    settings = di[Settings]

    library_repo = DBLibraryRepository()
    playlist_repo = DBPlaylistRepository()
    producer_conn_options = ProducerConnectionOptions(
        bootstrap_servers=settings.broker_bootstrap_server, client_id="producer-1"
    )
    playlist_consumer_conn_options = ConsumerConnectionOptions(
        bootstrap_servers=settings.broker_bootstrap_server,
        group_id="consumers-queue",
        client_id="consumer-1",
    )
    library_schema_config = SchemaRegistryConfig(
        url=settings.schema_registry_url,
        topic_name="library",
        schema_id="latest",
        subject_name="library-value",
    )
    playlist_schema_config = SchemaRegistryConfig(
        url=settings.schema_registry_url,
        topic_name="queue",
        schema_id="latest",
        subject_name="queue-value",
    )
    producer_msg_options = ProducerMessagesOptions(
        key_serializer=StringSerializer("utf_8"), value_serializer=serialize_event
    )
    consumer_msg_options = ConsumerMessagesOptions(value_deserializer=parse_event)
    library_events_producer = KafkaAvroEventsProducer(
        producer_conn_options, producer_msg_options, library_schema_config
    )
    playlist_events_producer = KafkaAvroEventsProducer(
        producer_conn_options, producer_msg_options, playlist_schema_config
    )
    playlist_events_consumer = KafkaAvroEventsConsumer(
        playlist_consumer_conn_options, consumer_msg_options, playlist_schema_config
    )

    di[Clock] = clock
    di[LibraryEventsProducer] = library_events_producer
    di[PlaylistEventsProducer] = playlist_events_producer
    di[PlaylistEventsConsumer] = playlist_events_consumer

    di[Library] = Library(library_repo, library_events_producer, clock)
    di[Playlist] = Playlist(
        playlist_repo,
        playlist_events_producer,
        playlist_events_consumer,
        clock,
    )
    di[RequestsService] = RequestsService(
        library_repo,
        playlist_repo,
        library_events_producer,
        playlist_events_producer,
        playlist_events_consumer,
        config,
        clock,
    )

    di[YoutubeAPIInterface] = YoutubeAPI()
    di[YoutubeTrackProvided] = YoutubeAPI

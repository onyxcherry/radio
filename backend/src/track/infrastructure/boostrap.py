from kink import di
from track.domain.events.utils.create import event_from_dict
from track.infrastructure.messaging.types import (
    LibraryEventsProducer,
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)
from track.application.interfaces.events import (
    ConsumerConnectionOptions,
    ConsumerMessagesOptions,
    ProducerConnectionOptions,
    ProducerMessagesOptions,
)
from track.infrastructure.messaging.kafka_events_consumer import KafkaAvroEventsConsumer
from track.infrastructure.messaging.kafka_events_producer import KafkaAvroEventsProducer
from track.infrastructure.messaging.schema_utils import SchemaRegistryConfig
from track.application.library import Library
from track.application.playlist import Playlist
from track.domain.providers.youtube import YoutubeTrackProvided
from track.infrastructure.db_library_repository import DBLibraryRepository
from track.infrastructure.db_playlist_repository import DBPlaylistRepository
from building_blocks.clock import Clock, SystemClock
from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.infrastructure.youtube_api import YoutubeAPI
from track.application.requests_service import RequestsService

from confluent_kafka.serialization import StringSerializer


def boostrap_di() -> None:
    clock = SystemClock()
    library_repo = DBLibraryRepository()
    playlist_repo = DBPlaylistRepository()
    producer_conn_options = ProducerConnectionOptions(
        bootstrap_servers="localhost:19092", client_id="producer-1"
    )
    playlist_consumer_conn_options = ConsumerConnectionOptions(
        bootstrap_servers="localhost:19092",
        group_id="consumers-queue",
        client_id="consumer-1",
    )
    library_schema_config = SchemaRegistryConfig(
        url="http://localhost:18081",
        topic_name="library",
        schema_id="latest",
        subject_name="library-value",
    )
    playlist_schema_config = SchemaRegistryConfig(
        url="http://localhost:18081",
        topic_name="queue",
        schema_id="latest",
        subject_name="queue-value",
    )
    producer_msg_options = ProducerMessagesOptions(
        key_serializer=StringSerializer("utf_8"), value_serializer=None
    )
    consumer_msg_options = ConsumerMessagesOptions(value_deserializer=event_from_dict)
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
        clock,
    )

    di[YoutubeAPIInterface] = YoutubeAPI()
    di[YoutubeTrackProvided] = YoutubeAPI

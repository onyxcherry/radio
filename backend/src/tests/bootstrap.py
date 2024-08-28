from kink import di
from track.domain.events.recreate import parse_event
from track.domain.events.serialize import serialize_event
from track.infrastructure.messaging.types import (
    LibraryEventsConsumer,
    LibraryEventsProducer,
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)
from track.infrastructure.messaging.schema_utils import SchemaRegistryConfig
from track.application.interfaces.events import (
    ConsumerConnectionOptions,
    ConsumerMessagesOptions,
    ProducerMessagesOptions,
    ProducerConnectionOptions,
)
from track.infrastructure.messaging.inmemory_events_consumer import (
    InMemoryEventsConsumer,
)
from track.infrastructure.messaging.inmemory_events_producer import (
    InMemoryEventsProducer,
)
from track.infrastructure.messaging.kafka_events_consumer import (
    KafkaAvroEventsConsumer,
)
from track.infrastructure.messaging.kafka_events_producer import (
    KafkaAvroEventsProducer,
)
from track.infrastructure.db_library_repository import DBLibraryRepository
from track.infrastructure.db_playlist_repository import DBPlaylistRepository
from track.application.playlist import Playlist
from track.application.library import Library
from track.domain.providers.youtube import YoutubeTrackProvided
from building_blocks.clock import Clock, FixedClock
from track.application.requests_service import RequestsService
from track.infrastructure.inmemory_library_repository import (
    InMemoryLibraryRepository,
)
from track.infrastructure.inmemory_playlist_repository import (
    InMemoryPlaylistRepository,
)
from tests.inmemory_youtube_api import InMemoryYoutubeAPI
from track.application.interfaces.youtube_api import YoutubeAPIInterface

from confluent_kafka.serialization import StringSerializer

from tests.helpers.dt import fixed_dt


def bootstrap_di(real_db: bool, real_msg_broker: bool) -> None:
    fixed_clock = FixedClock(fixed_dt)
    di[Clock] = fixed_clock

    if real_db:
        library_repo = DBLibraryRepository()
        playlist_repo = DBPlaylistRepository()
    else:
        library_repo = InMemoryLibraryRepository()
        playlist_repo = InMemoryPlaylistRepository()

    if real_msg_broker:
        producer_conn_options = ProducerConnectionOptions(
            bootstrap_servers="localhost:19092", client_id="producer-tests-1"
        )
        playlist_consumer_conn_options = ConsumerConnectionOptions(
            bootstrap_servers="localhost:19092",
            group_id="consumers-queue",
            client_id="consumer-tests-1",
        )
        library_consumer_conn_options = ConsumerConnectionOptions(
            bootstrap_servers="localhost:19092",
            group_id="consumers-library",
            client_id="consumer-tests-2",
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
            key_serializer=StringSerializer("utf_8"), value_serializer=serialize_event
        )
        consumer_msg_options = ConsumerMessagesOptions(value_deserializer=parse_event)
        library_events_producer = KafkaAvroEventsProducer(
            producer_conn_options, producer_msg_options, library_schema_config
        )
        library_events_consumer = KafkaAvroEventsConsumer(
            library_consumer_conn_options, consumer_msg_options, library_schema_config
        )
        playlist_events_producer = KafkaAvroEventsProducer(
            producer_conn_options, producer_msg_options, playlist_schema_config
        )
        playlist_events_consumer = KafkaAvroEventsConsumer(
            playlist_consumer_conn_options, consumer_msg_options, playlist_schema_config
        )
    else:
        producer_conn_options = ProducerConnectionOptions(
            bootstrap_servers="", client_id=""
        )
        consumer_conn_options = ConsumerConnectionOptions(
            bootstrap_servers="", group_id="", client_id=""
        )
        library_schema_config = SchemaRegistryConfig(
            url="",
            topic_name="library",
            schema_id="latest",
            subject_name="library-value",
        )
        playlist_schema_config = SchemaRegistryConfig(
            url="",
            topic_name="queue",
            schema_id="latest",
            subject_name="queue-value",
        )
        producer_msg_options = ProducerMessagesOptions(lambda x: x, lambda x: x)
        consumer_msg_options = ConsumerMessagesOptions(value_deserializer=lambda x: x)
        playlist_events_consumer = InMemoryEventsConsumer(
            consumer_conn_options, consumer_msg_options, playlist_schema_config
        )
        library_events_producer = InMemoryEventsProducer(
            producer_conn_options, producer_msg_options, library_schema_config
        )
        library_events_consumer = InMemoryEventsConsumer(
            consumer_conn_options, consumer_msg_options, library_schema_config
        )
        playlist_events_producer = InMemoryEventsProducer(
            producer_conn_options, producer_msg_options, playlist_schema_config
        )
        playlist_events_consumer = InMemoryEventsConsumer(
            consumer_conn_options, consumer_msg_options, playlist_schema_config
        )

    di[LibraryEventsProducer] = library_events_producer
    di[LibraryEventsConsumer] = library_events_consumer
    di[PlaylistEventsProducer] = playlist_events_producer
    di[PlaylistEventsConsumer] = playlist_events_consumer

    di[Library] = Library(library_repo, library_events_producer, fixed_clock)
    di[Playlist] = Playlist(
        playlist_repo,
        playlist_events_producer,
        playlist_events_consumer,
        fixed_clock,
    )
    di[RequestsService] = RequestsService(
        library_repo,
        playlist_repo,
        library_events_producer,
        playlist_events_producer,
        playlist_events_consumer,
        fixed_clock,
    )

    di[YoutubeAPIInterface] = InMemoryYoutubeAPI()
    di[YoutubeTrackProvided] = InMemoryYoutubeAPI

import datetime
import zoneinfo
from track.domain.provided import Seconds
from config import BreakData, BreaksConfig, Config, DurationRange, TracksConfig
from kink import di
from track.infrastructure.messaging.inmemory_events_helper import InMemoryEvents
from tests.choices import DIChoices
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
from track.infrastructure.messaging.kafka_events_consumer import KafkaAvroEventsConsumer
from track.infrastructure.messaging.kafka_events_producer import KafkaAvroEventsProducer
from track.infrastructure.db_library_repository import DBLibraryRepository
from track.infrastructure.db_playlist_repository import DBPlaylistRepository
from track.application.playlist import Playlist
from track.application.library import Library
from track.domain.providers.youtube import YoutubeTrackProvided
from building_blocks.clock import Clock, FixedClock
from track.application.requests_service import RequestsService
from track.infrastructure.inmemory_library_repository import InMemoryLibraryRepository
from track.infrastructure.inmemory_playlist_repository import InMemoryPlaylistRepository
from tests.inmemory_youtube_api import InMemoryYoutubeAPI
from track.application.interfaces.youtube_api import YoutubeAPIInterface

from confluent_kafka.serialization import StringSerializer

from tests.helpers.dt import fixed_dt

config = Config(
    breaks=BreaksConfig(
        offset=datetime.timedelta(seconds=3),
        timezone=zoneinfo.ZoneInfo(key="Europe/Warsaw"),
        breaks=[
            BreakData(
                start=datetime.time(8, 30),
                duration=Seconds(600),
                end=datetime.time(8, 40),
            ),
            BreakData(
                start=datetime.time(9, 25),
                duration=Seconds(600),
                end=datetime.time(9, 35),
            ),
            BreakData(
                start=datetime.time(10, 20),
                duration=Seconds(600),
                end=datetime.time(10, 30),
            ),
            BreakData(
                start=datetime.time(11, 15),
                duration=Seconds(900),
                end=datetime.time(11, 30),
            ),
            BreakData(
                start=datetime.time(12, 15),
                duration=Seconds(600),
                end=datetime.time(12, 25),
            ),
            BreakData(
                start=datetime.time(13, 10),
                duration=Seconds(600),
                end=datetime.time(13, 20),
            ),
            BreakData(
                start=datetime.time(14, 5),
                duration=Seconds(600),
                end=datetime.time(14, 15),
            ),
            BreakData(
                start=datetime.time(15, 0),
                duration=Seconds(600),
                end=datetime.time(15, 10),
            ),
        ],
    ),
    tracks=TracksConfig(
        duration=DurationRange(minimum=Seconds(20), maximum=Seconds(1200)),
        playing_duration_min=60,
        queued_one_break_max=8,
    ),
)


def bootstrap_di(di_choices: DIChoices) -> None:
    di[DIChoices] = di_choices
    fixed_clock = FixedClock(fixed_dt)
    di[Clock] = fixed_clock
    di[Config] = config

    if di_choices.real_db:
        library_repo = DBLibraryRepository()
        playlist_repo = DBPlaylistRepository()
    else:
        library_repo = InMemoryLibraryRepository()
        playlist_repo = InMemoryPlaylistRepository()

    if di_choices.real_msg_broker:
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
        di[InMemoryEvents] = InMemoryEvents()
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
        config,
        fixed_clock,
    )

    di[YoutubeAPIInterface] = InMemoryYoutubeAPI()
    di[YoutubeTrackProvided] = InMemoryYoutubeAPI

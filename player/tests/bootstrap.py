from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from confluent_kafka.serialization import StringSerializer
from kink import di

from application.break_observer import BreakObserver
from application.events.handle import EventHandler
from application.interfaces.events import (
    ConsumerConnectionOptions,
    ConsumerMessagesOptions,
    ProducerConnectionOptions,
    ProducerMessagesOptions,
)
from application.playing_manager import PlayingConditions, PlayingManager
from application.playing_observer import PlayingObserver
from application.track_file_provider import (
    PlayableTrackProvider,
    PlayableTrackProviderConfig,
)
from bootstrap import bootstrap_config
from building_blocks.awakable import EventBasedAwakable
from building_blocks.clock import Clock, FeignedWallClock
from config import BreakData, BreaksConfig, Settings
from domain.breaks import Breaks
from domain.events.recreate import parse_event
from domain.events.serialize import serialize_event
from domain.interfaces.player import Player
from domain.repositories.scheduled_tracks import ScheduledTracksRepository
from domain.types import Seconds
from infrastructure.madeup_player import MadeupPlayer
from infrastructure.messaging.inmemory_events_consumer import (
    InMemoryEventsConsumer,
)
from infrastructure.messaging.inmemory_events_helper import InMemoryEvents
from infrastructure.messaging.inmemory_events_producer import (
    InMemoryEventsProducer,
)
from infrastructure.messaging.kafka_events_consumer import (
    KafkaAvroEventsConsumer,
)
from infrastructure.messaging.kafka_events_producer import (
    KafkaAvroEventsProducer,
)
from infrastructure.messaging.schema_utils import SchemaRegistryConfig
from infrastructure.messaging.types import (
    LibraryEventsConsumer,
    LibraryEventsProducer,
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)
from infrastructure.persistence.db_scheduled_tracks_repository import (
    DBScheduledTracksRepository,
)
from infrastructure.persistence.inmemory_scheduled_tracks_repository import (
    InMemoryScheduledTracksRepository,
)

from .choices import DIChoices


def create_breaks_config() -> BreaksConfig:
    breaks_config = BreaksConfig(
        breaks=[
            BreakData(start=time(8, 30), duration=Seconds(10 * 60)),
            BreakData(start=time(9, 25), duration=Seconds(10 * 60)),
            BreakData(start=time(10, 20), duration=Seconds(10 * 60)),
            BreakData(start=time(11, 15), duration=Seconds(15 * 60)),
            BreakData(start=time(12, 15), duration=Seconds(10 * 60)),
            BreakData(start=time(13, 10), duration=Seconds(10 * 60)),
            BreakData(start=time(14, 5), duration=Seconds(10 * 60)),
            BreakData(start=time(15, 00), duration=Seconds(10 * 60)),
        ],
        offset=timedelta(seconds=17),
        timezone=ZoneInfo("Europe/Warsaw"),
    )
    return breaks_config


def reregister_deps_with_clock(clock: Clock):
    di_choices = di[DIChoices]

    breaks = Breaks(create_breaks_config(), clock)
    di[Breaks] = breaks
    break_observer = BreakObserver(breaks=breaks, clock=clock)
    di[BreakObserver] = break_observer

    if di_choices.real_db:
        scheduled_tracks_repo = DBScheduledTracksRepository(clock=clock)
    else:
        scheduled_tracks_repo = InMemoryScheduledTracksRepository(clock=clock)

    di[ScheduledTracksRepository] = scheduled_tracks_repo

    playing_observer = PlayingObserver(
        breaks=breaks, scheduled_tracks_repo=scheduled_tracks_repo, clock=clock
    )
    di[PlayingObserver] = playing_observer
    playable_track_provider = PlayableTrackProvider(
        config=di[PlayableTrackProviderConfig],
        scheduled_tracks_repo=scheduled_tracks_repo,
        clock=clock,
    )
    di[PlayableTrackProvider] = playable_track_provider

    playing_manager = PlayingManager(
        playing_observer,
        break_observer,
        di[PlayingConditions],
        playable_track_provider,
        di[Player],
    )
    di[PlayingManager] = playing_manager
    di[EventHandler] = EventHandler(
        breaks=breaks, scheduled_tracks_repo=scheduled_tracks_repo, clock=clock
    )


def bootstrap_di(di_choices: DIChoices) -> None:
    bootstrap_config()
    settings = di[Settings]

    di[DIChoices] = di_choices
    breaks_config = create_breaks_config()
    dt = datetime(2024, 8, 1, 8, 34, 11, tzinfo=breaks_config.timezone)
    # clock = FixedClock(dt)
    clock = FeignedWallClock(dt)
    di[Clock] = clock
    player = MadeupPlayer()
    di[Player] = player
    di[BreaksConfig] = breaks_config

    playable_track_provider_config = PlayableTrackProviderConfig(
        Path((Path(__file__).parent / "data").absolute())
    )
    di[PlayableTrackProviderConfig] = playable_track_provider_config

    playing_conditions = PlayingConditions(
        manually_stopped=EventBasedAwakable(),
        stopped_due_to_tech_error=EventBasedAwakable(),
    )
    di[PlayingConditions] = playing_conditions

    reregister_deps_with_clock(clock)

    if di_choices.real_msg_broker:
        producer_conn_options = ProducerConnectionOptions(
            bootstrap_servers=settings.broker_bootstrap_server,
            client_id="producer-tests-1",
        )
        playlist_consumer_conn_options = ConsumerConnectionOptions(
            bootstrap_servers=settings.broker_bootstrap_server,
            group_id="consumers-player-queue",
            client_id="consumer-player-queue-tests-1",
        )
        library_consumer_conn_options = ConsumerConnectionOptions(
            bootstrap_servers=settings.broker_bootstrap_server,
            group_id="consumers-player-library",
            client_id="consumer-player-library-tests-1",
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
            # schema_id=17,
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

    library_events_consumer.subscribe("library")
    playlist_events_consumer.subscribe("queue")

    di[LibraryEventsProducer] = library_events_producer
    di[LibraryEventsConsumer] = library_events_consumer
    di[PlaylistEventsProducer] = playlist_events_producer
    di[PlaylistEventsConsumer] = playlist_events_consumer

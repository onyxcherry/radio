from datetime import datetime
from pathlib import Path
from kink import di


from player.src.application.break_observer import BreakObserver
from player.src.application.events.handle import EventHandler
from player.src.application.playing_manager import PlayingConditions, PlayingManager
from player.src.application.playing_observer import PlayingObserver
from player.src.application.track_file_provider import (
    PlayableTrackProvider,
    PlayableTrackProviderConfig,
)
from player.src.building_blocks.awakable import EventBasedAwakable
from player.src.infrastructure.messaging.inmemory_events_helper import InMemoryEvents
from player.src.infrastructure.messaging.types import (
    LibraryEventsConsumer,
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)
from player.src.application.interfaces.events import (
    ProducerMessagesOptions,
    ConsumerMessagesOptions,
)
from player.src.application.interfaces.events import (
    ConsumerConnectionOptions,
    ProducerConnectionOptions,
)
from player.src.building_blocks.clock import Clock, FeignedWallClock
from player.src.config import BreaksConfig
from player.src.domain.breaks import Breaks
from player.src.domain.interfaces.player import Player
from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository
from player.src.infrastructure.madeup_player import MadeupPlayer
from player.src.infrastructure.messaging.inmemory_events_consumer import (
    InMemoryEventsConsumer,
)
from player.src.infrastructure.messaging.inmemory_events_producer import (
    InMemoryEventsProducer,
)
from player.src.infrastructure.messaging.kafka_events_consumer import (
    KafkaAvroEventsConsumer,
)
from player.src.infrastructure.messaging.kafka_events_producer import (
    KafkaAvroEventsProducer,
)
from player.src.infrastructure.messaging.schema_utils import SchemaRegistryConfig
from player.src.infrastructure.messaging.types import LibraryEventsProducer
from player.src.infrastructure.persistence.db_scheduled_tracks_repository import (
    DBScheduledTracksRepository,
)
from player.src.infrastructure.persistence.inmemory_scheduled_tracks_repository import (
    InMemoryScheduledTracksRepository,
)
from confluent_kafka.serialization import StringSerializer

from player.tests.choices import DIChoices, breaks_config


def reregister_deps_with_clock(clock: Clock):
    di_choices = di[DIChoices]

    breaks = Breaks(breaks_config, clock)
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
    di[DIChoices] = di_choices
    dt = datetime(2024, 8, 1, 8, 34, 11, tzinfo=breaks_config.timezone)
    # clock = FixedClock(dt)
    clock = FeignedWallClock(dt)
    di[Clock] = clock
    player = MadeupPlayer()
    di[Player] = player
    di[BreaksConfig] = breaks_config

    test_data_dir = Path("/home/tomasz/radio/player/tests/data/")
    playable_track_provider_config = PlayableTrackProviderConfig(test_data_dir)
    di[PlayableTrackProviderConfig] = playable_track_provider_config

    playing_conditions = PlayingConditions(
        manually_stopped=EventBasedAwakable(),
        stopped_due_to_tech_error=EventBasedAwakable(),
    )
    di[PlayingConditions] = playing_conditions

    reregister_deps_with_clock(clock)

    if di_choices.real_msg_broker and False:
        producer_conn_options = ProducerConnectionOptions(
            bootstrap_servers="localhost:19092", client_id="producer-tests-1"
        )
        playlist_consumer_conn_options = ConsumerConnectionOptions(
            bootstrap_servers="localhost:19092",
            group_id="consumers-player-queue",
            client_id="consumer-player-queue-tests-1",
        )
        library_consumer_conn_options = ConsumerConnectionOptions(
            bootstrap_servers="localhost:19092",
            group_id="consumers-player-library",
            client_id="consumer-player-library-tests-1",
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
        consumer_msg_options = ConsumerMessagesOptions(
            value_deserializer=event_from_dict
        )
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

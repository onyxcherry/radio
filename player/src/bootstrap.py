from datetime import time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from kink import di


from application.break_observer import BreakObserver
from application.events.handle import EventHandler
from application.playing_manager import PlayingConditions, PlayingManager
from application.playing_observer import PlayingObserver
from application.track_file_provider import (
    PlayableTrackProvider,
    PlayableTrackProviderConfig,
)
from building_blocks.awakable import EventBasedAwakable
from config import Settings, config_dict_to_class, load_config_from_yaml
from building_blocks.clock import Clock, SystemClock
from config import BreaksConfig
from domain.breaks import Breaks
from domain.events.recreate import parse_event
from domain.events.serialize import serialize_event
from domain.interfaces.player import Player
from domain.repositories.scheduled_tracks import ScheduledTracksRepository
from domain.types import Seconds
from infrastructure.madeup_player import MadeupPlayer
from infrastructure.persistence.db_scheduled_tracks_repository import (
    DBScheduledTracksRepository,
)
from infrastructure.messaging.types import (
    LibraryEventsConsumer,
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)
from application.interfaces.events import (
    ProducerMessagesOptions,
    ConsumerMessagesOptions,
)
from application.interfaces.events import (
    ConsumerConnectionOptions,
    ProducerConnectionOptions,
)
from building_blocks.clock import Clock
from config import BreaksConfig
from domain.breaks import Breaks
from domain.interfaces.player import Player
from domain.repositories.scheduled_tracks import ScheduledTracksRepository
from domain.types import Seconds
from infrastructure.madeup_player import MadeupPlayer
from infrastructure.messaging.inmemory_events_consumer import (
    InMemoryEventsConsumer,
)
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
from infrastructure.messaging.types import LibraryEventsProducer
from infrastructure.persistence.db_scheduled_tracks_repository import (
    DBScheduledTracksRepository,
)
from confluent_kafka.serialization import StringSerializer


CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.yaml"
CONFIG_SCHEMA_PATH = Path(__file__).parent.parent / "config.schema.json"


def bootstrap_di():
    clock = SystemClock()
    di[Clock] = clock

    player = MadeupPlayer()
    di[Player] = player

    config_dict = load_config_from_yaml(
        config_path=CONFIG_FILE_PATH, schema_path=CONFIG_SCHEMA_PATH
    )
    settings = Settings()  # type: ignore
    config = config_dict_to_class(config_dict)
    breaks_config = config.breaks
    di[BreaksConfig] = breaks_config
    breaks = Breaks(breaks_config, clock)
    di[Breaks] = breaks
    break_observer = BreakObserver(breaks=breaks, clock=clock)
    di[BreakObserver] = break_observer

    scheduled_tracks_repo = DBScheduledTracksRepository(clock=clock)
    di[ScheduledTracksRepository] = scheduled_tracks_repo

    playable_track_provider_config = PlayableTrackProviderConfig(
        Path(settings.tracks_files_path)
    )
    di[PlayableTrackProviderConfig] = playable_track_provider_config

    playing_conditions = PlayingConditions(
        manually_stopped=EventBasedAwakable(),
        stopped_due_to_tech_error=EventBasedAwakable(),
    )
    di[PlayingConditions] = playing_conditions

    playing_observer = PlayingObserver(
        breaks=breaks, scheduled_tracks_repo=scheduled_tracks_repo, clock=clock
    )
    di[PlayingObserver] = playing_observer
    playable_track_provider = PlayableTrackProvider(
        config=playable_track_provider_config,
        scheduled_tracks_repo=scheduled_tracks_repo,
        clock=clock,
    )
    di[PlayableTrackProvider] = playable_track_provider

    playing_manager = PlayingManager(
        playing_observer,
        break_observer,
        playing_conditions,
        playable_track_provider,
        player,
    )
    di[PlayingManager] = playing_manager
    di[EventHandler] = EventHandler(
        breaks=breaks, scheduled_tracks_repo=scheduled_tracks_repo, clock=clock
    )

    producer_conn_options = ProducerConnectionOptions(
        bootstrap_servers=settings.broker_bootstrap_server, client_id="producer-1"
    )
    playlist_consumer_conn_options = ConsumerConnectionOptions(
        bootstrap_servers=settings.broker_bootstrap_server,
        group_id="consumers-player-queue",
        client_id="consumer-player-queue-1",
    )
    library_consumer_conn_options = ConsumerConnectionOptions(
        bootstrap_servers=settings.broker_bootstrap_server,
        group_id="consumers-player-library",
        client_id="consumer-player-library-1",
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
    library_events_consumer = KafkaAvroEventsConsumer(
        library_consumer_conn_options, consumer_msg_options, library_schema_config
    )
    playlist_events_producer = KafkaAvroEventsProducer(
        producer_conn_options, producer_msg_options, playlist_schema_config
    )
    playlist_events_consumer = KafkaAvroEventsConsumer(
        playlist_consumer_conn_options, consumer_msg_options, playlist_schema_config
    )

    di[LibraryEventsProducer] = library_events_producer
    di[LibraryEventsConsumer] = library_events_consumer
    di[PlaylistEventsProducer] = playlist_events_producer
    di[PlaylistEventsConsumer] = playlist_events_consumer

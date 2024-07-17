from datetime import datetime
from kink import di
from track.application.interfaces.events import EventsConsumer, EventsProducer
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
from track.domain.library_repository import LibraryRepository
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

fixed_dt = datetime(2024, 7, 16, 14, 19, 21)


def bootstrap_di(real_db: bool, real_msg_broker: bool) -> None:
    fixed_clock = FixedClock(fixed_dt)
    di[Clock] = fixed_clock

    if real_db:
        library_repo = DBLibraryRepository()
        playlist_repo = DBPlaylistRepository()
    else:
        library_repo = InMemoryLibraryRepository()
        playlist_repo = InMemoryPlaylistRepository()

    if real_msg_broker and False:
        events_producer = KafkaAvroEventsProducer()
        events_consumer = KafkaAvroEventsConsumer()
    else:
        events_consumer = InMemoryEventsConsumer()
        events_producer = InMemoryEventsProducer()

    di[EventsProducer] = events_producer
    di[EventsConsumer] = events_consumer

    di[Library] = Library(library_repo, events_producer, fixed_clock)
    di[Playlist] = Playlist(
        playlist_repo,
        events_producer,
        events_consumer,
        fixed_clock,
    )
    di[RequestsService] = RequestsService(
        library_repo,
        playlist_repo,
        events_producer,
        events_consumer,
        fixed_clock,
    )

    di[YoutubeAPIInterface] = InMemoryYoutubeAPI()
    di[YoutubeTrackProvided] = InMemoryYoutubeAPI

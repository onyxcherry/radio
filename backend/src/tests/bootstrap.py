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

UNIT = True

fixed_dt = datetime(2024, 7, 16, 14, 19, 21)


def bootstrap_di() -> None:
    fixed_clock = FixedClock(fixed_dt)
    di[Clock] = fixed_clock
    if UNIT:
        inmemory_library_repo = InMemoryLibraryRepository()
        inmemory_playlist_repo = InMemoryPlaylistRepository()
        inmemory_events_consumer = InMemoryEventsConsumer()
        inmemory_events_producer = InMemoryEventsProducer()
        di[EventsProducer] = inmemory_events_producer
        di[EventsConsumer] = inmemory_events_consumer
        di[Library] = Library(
            inmemory_library_repo, inmemory_events_producer, fixed_clock
        )
        di[Playlist] = Playlist(
            inmemory_playlist_repo,
            inmemory_events_producer,
            inmemory_events_consumer,
            fixed_clock,
        )
        di[RequestsService] = RequestsService(
            inmemory_library_repo,
            inmemory_playlist_repo,
            inmemory_events_producer,
            inmemory_events_consumer,
            fixed_clock,
        )
    elif False:
        real_library_repo = DBLibraryRepository()
        real_playlist_repo = DBPlaylistRepository()
        real_events_producer = KafkaAvroEventsProducer()
        real_events_consumer = KafkaAvroEventsConsumer()
        di[Library] = Library(real_library_repo, real_events_producer, fixed_clock)
        di[Playlist] = Playlist(
            real_playlist_repo,
            real_events_producer,
            real_events_consumer,
            fixed_clock,
        )
        di[RequestsService] = RequestsService(
            real_library_repo,
            real_playlist_repo,
            real_events_producer,
            real_events_consumer,
            fixed_clock,
        )
    di[YoutubeAPIInterface] = InMemoryYoutubeAPI()
    di[YoutubeTrackProvided] = InMemoryYoutubeAPI

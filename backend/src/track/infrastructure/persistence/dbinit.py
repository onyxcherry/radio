from track.infrastructure.persistence.database import engine
from track.application.models.base import Base
from track.application.models.library import LibraryTrackModel  # noqa
from track.application.models.queue import QueueTrackModel  # noqa

# https://stackoverflow.com/a/73639613/14011471

Base.metadata.create_all(bind=engine)
print(Base.metadata)

from track.infrastructure.persistence.database import engine
from track.application.models.base import Base
from track.application.models.library import TrackModel  # noqa
from track.application.models.queue import QueuedTrackModel  # noqa

# https://stackoverflow.com/a/73639613/14011471
# turbo dziwne, ale trzeba zaimportować te modele, by się stworzyły

Base.metadata.create_all(bind=engine)
print(Base.metadata)

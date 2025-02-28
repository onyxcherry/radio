from track.application.models.base import Base
from track.application.models.library import LibraryTrackModel  # noqa
from track.application.models.queue import QueueTrackModel  # noqa
from track.infrastructure.persistence.database import setup_engine


# https://stackoverflow.com/a/73639613/14011471
def main():
    Base.metadata.create_all(bind=setup_engine())


if __name__ == "__main__":
    main()

from application.models.base import Base
from infrastructure.persistence.database import setup_engine
from application.models.scheduled_tracks import ScheduledTrackModel  # noqa


def main():
    Base.metadata.create_all(bind=setup_engine())


if __name__ == "__main__":
    main()

from application.models.base import Base
from infrastructure.persistence.database import engine
from application.models.scheduled_tracks import ScheduledTrackModel  # noqa


def main():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()

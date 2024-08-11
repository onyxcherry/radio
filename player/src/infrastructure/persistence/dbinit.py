from player.src.application.models.base import Base
from player.src.infrastructure.persistence.database import engine
from player.src.application.models.scheduled_tracks import ScheduledTrackModel  # noqa

Base.metadata.create_all(bind=engine)
print(Base.metadata)

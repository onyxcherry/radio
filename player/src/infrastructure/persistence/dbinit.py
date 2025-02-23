from application.models.base import Base
from infrastructure.persistence.database import engine
from application.models.scheduled_tracks import ScheduledTrackModel  # noqa

Base.metadata.create_all(bind=engine)
print(Base.metadata)

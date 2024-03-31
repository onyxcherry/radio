from datetime import date
from track.application.models.library import QueuedTrackModel, TrackModel
from track.domain.status import Status
from track.infrastructure.persistence.database import SessionLocal

session = SessionLocal()
new_track = TrackModel(
    provider="youtube",
    identifier="pp0TTI0rRnE",
    status=Status.PENDING_APPROVAL.value,
)
d = date(2024, 3, 28)
scheduled_track = QueuedTrackModel(
    date_=d,
    break_=2,
    identifier="pp0TTI0rRnE",
    provider="youtube",
    played=False,
)
session.add(new_track)
session.add(scheduled_track)
session.commit()

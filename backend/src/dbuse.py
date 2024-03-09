from track.application.models.library import Library
from track.domain.status import Status
from track.infrastructure.persistence.database import SessionLocal

session = SessionLocal()
new_track = Library(
    provider="youtube", identifier="pp0TTI0rRnE", status=Status.PENDING_APPROVAL.value
)
session.add(new_track)
session.commit()

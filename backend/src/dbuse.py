from datetime import date

from sqlalchemy import select
from track.application.models.library import TrackModel
from track.application.models.queue import QueuedTrackModel
from track.domain.status import Status
from track.infrastructure.persistence.database import SessionLocal


def add_data():
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
        track_id=1,
    )
    session.add(new_track)
    session.add(scheduled_track)
    session.commit()


# add_data()
# def search_for():
session = SessionLocal()
result = session.execute(select(QueuedTrackModel).order_by(QueuedTrackModel.id)).all()
print(result)


# search_for()
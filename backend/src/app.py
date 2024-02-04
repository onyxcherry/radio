import datetime
from kink import di
from track.domain.breaks import BreaksEnum
from track.application.dto import TrackRequestedAt
from track.application.playlist import PlayingTime
from track.application.requests_service import RequestsService

rs = di[RequestsService]

url = "cokolwiek"
pt = PlayingTime(
    break_=BreaksEnum.SECOND,
    date_=datetime.datetime.now().date() + datetime.timedelta(days=1),
)
tra = TrackRequestedAt(url=url, when=pt)
rs.request(tra)

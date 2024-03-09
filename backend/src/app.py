import datetime
from kink import di
from track.domain.providers.youtube import YoutubeTrackProvider
from track.domain.breaks import BreaksEnum
from track.application.dto import TrackRequestedAt
from track.application.playlist import PlayingTime
from track.application.requests_service import RequestsService

from track.boostrap import boostrap_di

boostrap_di()
rs = di[RequestsService]

url = "https://www.youtube.com/watch?v=rDMBzMcRuMg"
pt = PlayingTime(
    break_=BreaksEnum.SECOND,
    date_=datetime.datetime.now().date() + datetime.timedelta(days=1),
)
tra = TrackRequestedAt(url=url, when=pt)
rs.request(tra)

print(YoutubeTrackProvider.get_track_id(url))

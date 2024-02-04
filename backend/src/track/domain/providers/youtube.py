from datetime import timedelta
import string
from track.domain.errors import TrackIdentifierError
from track.domain.status import ErrorMessages
from track.infrastructure.config import get_logger
from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.domain.duration import parse_isoduration
from track.domain.track import Seconds, TrackId, TrackProvider, TrackUrl

from urllib.parse import parse_qs
import urllib.parse as urlparse


logger = get_logger(__name__)

ORIGINS = ["youtube.com", "m.youtube.com", "www.youtube.com", "youtu.be"]


class YoutubeTrackProvider(TrackProvider):
    _provider = "Youtube"

    def __init__(self, url: TrackUrl, api: YoutubeAPIInterface) -> None:
        self._id = self.get_track_id(url)
        self._url = self.build_standard_url(self._id)
        self._api = api

    @property
    def identity(self) -> TrackId:
        return self._id

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def url(self) -> TrackUrl:
        return self._url

    @property
    def title(self) -> str:
        if self._title is None:
            self._title = self.get_title()
        return self._title

    @property
    def duration(self) -> Seconds:
        if self._duration is None:
            self._duration = self.get_duration()
        return self._duration

    async def fetch_all_properties(self) -> None:
        if self._title is None:
            self._title = self.get_title()
        if self._duration is None:
            self._duration = self.get_duration()

    def __str__(self) -> str:
        return f'YoutubeTrack("{self._url}")'

    def __repr__(self) -> str:
        return (
            f"<YoutubeTrack id={self._id} url={self._url} "
            + f"{self._duration=} {self._title=}>"
        )

    # def __eq__(self, other) -> bool:
    #     if isinstance(other, YoutubeTrack):
    #         return self._url == other.url
    #     return False

    @classmethod
    def check_url_valid(cls, url: str):
        if cls._check_video_id(url):
            # przekazywać pełny url (bądź w przyszłości (id, provider))
            return False

    @classmethod
    def get_track_id(cls, url: str) -> TrackId:
        if cls._check_video_id(url):
            track_id = TrackId(url)
            return track_id

        parsed_url = urlparse.urlparse(url)

        if (
            parsed_url.netloc in ["youtube.com", "m.youtube.com", "www.youtube.com"]
            and parsed_url.path == "/watch"
        ):
            v_param = parse_qs(parsed_url.query).get("v")
            if v_param and len(v_param) > 0 and cls._check_video_id(v_param[0]):
                track_id = TrackId(v_param[0])
                return track_id
        elif parsed_url.netloc == "youtu.be":
            track_id = TrackId(parsed_url.path[1:])
            if cls._check_video_id(track_id):
                return TrackId(track_id)
        raise TrackIdentifierError(ErrorMessages.INVALID_YOUTUBE_TRACK_URL)

    @staticmethod
    def build_standard_url(id_: TrackId) -> TrackUrl:
        base_url = "https://www.youtube.com/watch?"
        desired_parameters = {"v": id_}
        urlencoded_parameters = urlparse.urlencode(desired_parameters)
        standard_track_url = base_url + urlencoded_parameters
        return TrackUrl(standard_track_url)

    @staticmethod
    def _check_video_id(url: str) -> bool:
        id_charset = [*string.ascii_letters, *string.digits, "-", "_"]
        return len(url) == 11 and all(character in id_charset for character in url)

    def get_duration(self) -> Seconds:
        api_response = self._api.get_api_part(self._id, "contentDetails")
        iso_duration = api_response["duration"]
        assert isinstance(iso_duration, str)

        parsed_time = parse_isoduration(iso_duration)
        td = timedelta(**parsed_time)
        duration = Seconds(int(td.total_seconds()))
        self._duration = duration
        return self._duration

    def _check_channel_belongs_official_artist(self, channel_id: str) -> bool:
        channel_info = self._api.get_channel_info(channel_id)

        try:
            header_rendered = channel_info[1]["response"]["header"][
                "c4TabbedHeaderRenderer"
            ]
        except (IndexError, KeyError) as ex:
            logger.warning(f"Response does not contain expected keys - {ex}")
            raise ex

        if "badges" not in header_rendered:
            return False

        try:
            badge = header_rendered["badges"][0]
            badge_type = badge["metadataBadgeRenderer"]["icon"]["iconType"]
        except (IndexError, KeyError) as ex:
            logger.warning(f"Expected valid badge metadata - {ex}")
            raise ex
        else:
            return badge_type == "OFFICIAL_ARTIST_BADGE"

    def get_title(self) -> str:
        api_response = self._api.get_api_part(self._id, "snippet")
        track_title = api_response["title"]
        self._title = track_title

        delims = ["-", "–", "—", "|"]
        topic_suffix = "- Topic"
        if not any([ch in track_title for ch in delims]):
            channel_title: str = api_response["channelTitle"]
            channel_id: str = api_response["channelId"]
            if self._check_channel_belongs_official_artist(channel_id):
                author = channel_title
                full_title = f"{author} - {track_title}"
                self._title = full_title
            elif topic_suffix in channel_title:
                author = channel_title.removesuffix(topic_suffix).strip()
                full_title = f"{author} - {track_title}"
                self._title = full_title

        return self._title

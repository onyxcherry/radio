from datetime import timedelta
import string
from typing import Self

from kink import inject
from track.domain.errors import TrackIdentifierError
from track.domain.errors import ErrorMessages
from track.infrastructure.config import get_logger
from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.domain.duration import parse_isoduration
from track.domain.provided import (
    ProviderName,
    Seconds,
    Identifier,
    TrackProvided,
    TrackProvidedIdentity,
    TrackUrl,
)

from urllib.parse import parse_qs, unquote
import urllib.parse as urlparse


logger = get_logger(__name__)

_ORIGINS_WATCH_PATH = ["youtube.com", "m.youtube.com", "www.youtube.com"]
_ORIGINS_SHORT_PATH = ["youtu.be"]
_WATCH_PATH = "/watch"

ORIGINS = _ORIGINS_WATCH_PATH + _ORIGINS_SHORT_PATH


@inject
class YoutubeTrackProvided(TrackProvided):
    _provider = ProviderName("Youtube")

    def __init__(
        self,
        identifier: Identifier,
        api: YoutubeAPIInterface,
    ) -> None:
        self._id = identifier
        self._url = self.build_standard_url(identifier)
        self._api = api
        self._title = None
        self._duration = None

    @property
    def identity(self) -> TrackProvidedIdentity:
        return TrackProvidedIdentity(
            identifier=self.identifier,
            provider=self.provider,
        )

    @property
    def identifier(self) -> Identifier:
        return self._id

    @property
    def provider(self) -> ProviderName:
        return self._provider

    @property
    def url(self) -> TrackUrl:
        return self._url

    @property
    def title(self) -> str:
        if self._title is None:
            self._title = self._get_title()
        return self._title

    @property
    def duration(self) -> Seconds:
        if self._duration is None:
            self._duration = self._get_duration()
        return self._duration

    @classmethod
    def from_url(cls, url: TrackUrl, api: YoutubeAPIInterface) -> Self:
        id_ = cls.extract_id(url)
        return cls(id_, api)

    def __str__(self) -> str:
        return (
            f"YoutubeTrack(id={self._id!s}, url={self._url!s}, "
            + f"duration={self._duration!s}, title={self._title!s})"
        )

    def __repr__(self) -> str:
        return f"YoutubeTrack(url={self._url!r}, api={self._api!r})"

    # def __eq__(self, other) -> bool:
    #     if isinstance(other, YoutubeTrack):
    #         return self._url == other.url
    #     return False

    def _get_duration(self) -> Seconds:
        api_response = self._api.get_api_part(self._id, "contentDetails")
        # print(f"{api_response=}")
        iso_duration = api_response["duration"]
        assert isinstance(iso_duration, str)

        parsed_time = parse_isoduration(iso_duration)
        td = timedelta(**parsed_time)
        duration = Seconds(int(td.total_seconds()))
        return duration

    def _check_channel_belongs_official_artist(self, channel_id: str) -> bool:
        print("A tutaj też?")
        channel_info = self._api.get_channel_info(channel_id)
        try:
            header_rendered = channel_info[1]["response"]["header"][
                "c4TabbedHeaderRenderer"
            ]
        except (IndexError, KeyError) as ex:
            logger.warning(f"Response does not contain expected keys - {ex}")
            raise ex

        # print(f"{channel_info[1]["response"]["header"][
        #         "c4TabbedHeaderRenderer"
        #     ]=}")
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

    def _get_title(self) -> str:
        api_response = self._api.get_api_part(self._id, "snippet")
        # print(f"{api_response=}")
        track_title = api_response["title"]

        delims = ["-", "–", "—", "|"]
        topic_suffix = "- Topic"
        if not any([ch in track_title for ch in delims]):
            channel_title: str = api_response["channelTitle"]
            channel_id: str = api_response["channelId"]
            # if self._check_channel_belongs_official_artist(channel_id):
            #     author = channel_title
            #     full_title = f"{author} - {track_title}"
            #     self._title = full_title
            if topic_suffix in channel_title:
                author = channel_title.removesuffix(topic_suffix).strip()
                full_title = f"{author} - {track_title}"
                return full_title

            return channel_title

        return track_title

    @staticmethod
    def _check_video_id(id_: str) -> bool:
        id_charset = [*string.ascii_letters, *string.digits, "-", "_"]
        return len(id_) == 11 and all(character in id_charset for character in id_)

    @classmethod
    def extract_id(cls, url: str) -> Identifier:
        if not isinstance(url, str):
            raise TypeError(f"Passed {type(url)} type, expected 'str'")

        if cls._check_video_id(url):
            track_id = Identifier(url)
            return track_id

        unquoted = unquote(url)

        protocolful = unquoted

        if not protocolful.startswith(("http://", "https://")):
            protocolful = "https://" + protocolful

        parsed_url = urlparse.urlparse(protocolful)

        if parsed_url.netloc in _ORIGINS_WATCH_PATH and parsed_url.path == _WATCH_PATH:
            v_param = parse_qs(parsed_url.query).get("v")
            if v_param and len(v_param) > 0 and cls._check_video_id(v_param[0]):
                track_id = Identifier(v_param[0])
                return track_id
        elif parsed_url.netloc in _ORIGINS_SHORT_PATH:
            track_id = Identifier(parsed_url.path[1:])
            if cls._check_video_id(track_id):
                return Identifier(track_id)
        raise TrackIdentifierError(ErrorMessages.INVALID_YOUTUBE_TRACK_URL)

    @staticmethod
    def build_standard_url(id_: Identifier) -> TrackUrl:
        base_url = "https://www.youtube.com/watch?"
        desired_parameters = {"v": id_}
        urlencoded_parameters = urlparse.urlencode(desired_parameters)
        standard_track_url = base_url + urlencoded_parameters
        return TrackUrl(standard_track_url)

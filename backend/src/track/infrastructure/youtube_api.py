from json import JSONDecodeError
import requests

from track.infrastructure.config import Config, get_logger
from track.application.interfaces.youtube_api import YoutubeAPIInterface
from track.domain.provided import Identifier
from track.application.errors import (
    TrackAPIConfigurationError,
    TrackAPIConnectionError,
    TrackAPIMalformedResponse,
    TrackAPINoResults,
    TrackAPITimeout,
)

logger = get_logger(__name__)


class _PublicAPIProvider:
    @staticmethod
    def get_api_part(track_id: Identifier, part: str) -> dict:
        api_url = (
            f"{Config.YOUTUBE_API_URL}?part={part}&id={track_id}"
            f"&key={Config.YOUTUBE_API_KEY}"
        )
        try:
            resp = requests.get(api_url, timeout=(1, 3))
        except requests.exceptions.ConnectionError:
            raise TrackAPIConnectionError(f"Unable to connect to {api_url}")
        except requests.Timeout:
            raise TrackAPITimeout(
                f"Timeout occured during request to Youtube API "
                f"to fetch {part} part of id={track_id}"
            )
        try:
            json_response = resp.json()
        except JSONDecodeError:
            raise TrackAPIMalformedResponse(
                "An error occured during decoding response to request "
                + f"of Youtube's id={track_id} in {part} part"
            )

        # even if KeyError is thrown (so the response's JSON is malformed)
        # and has (not) been handled,
        # the server won't finally respond with anything other than HTTP 500
        if (
            "error" in json_response
            and "key not valid" in json_response["error"]["message"]
        ):
            message = "Passed Youtube API key not valid!"
            logger.error(message + " Verify its correctness in the configuration!")
            raise TrackAPIConfigurationError(message)

        results_count = json_response["pageInfo"]["totalResults"]
        if results_count == 0:
            raise TrackAPINoResults("Youtube API returns 0 tracks' info")

        requested_part_info = json_response["items"][0][part]
        return requested_part_info


class _InternalAPIProvider:
    @staticmethod
    def get_channel_info(channel_id: str) -> dict:
        headers = {
            "X-YouTube-Client-Name": "1",
            "X-YouTube-Client-Version": "2.20201021.03.00",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            + "AppleWebKit/ 537.36 (KHTML, like Gecko) "
            + "Chrome/105.0.5195.102 Safari/537.36",
        }

        internal_api_required_suffix = "channels?flow=grid&view=0&pbj=1"
        yt_channel_url = f"https://www.youtube.com/channel/{channel_id}/"
        url = yt_channel_url + internal_api_required_suffix

        response = requests.get(url, headers=headers)
        try:
            parsed = response.json()
        except requests.exceptions.JSONDecodeError as ex:
            logger.warning(
                f"Endpoint {url} with headers {headers}"
                + " returned JSON-unparsable response"
            )
            raise ex
        else:
            return parsed


class YoutubeAPI(
    _InternalAPIProvider,
    _PublicAPIProvider,
    YoutubeAPIInterface,
):
    pass

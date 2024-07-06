from enum import Enum


class ErrorMessages(Enum):
    UNKNOWN_PROVIDER = "Incompatible track url - we do not support this music provider"
    NO_TRACK_ID = "No track id"
    NO_TRACK_URL = "No track url"
    INVALID_YOUTUBE_TRACK_URL = "Incorrect Youtube track url - cannot extract track id"


class TrackIdentifierError(ValueError):
    pass

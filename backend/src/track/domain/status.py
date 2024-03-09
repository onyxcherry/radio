from enum import Enum, unique

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorMessages(Enum):
    UNKNOWN_PROVIDER = "Incompatible track url - we do not support this music provider"
    NO_TRACK_ID = "No track id"
    NO_TRACK_URL = "No track url"
    INVALID_YOUTUBE_TRACK_URL = "Incorrect Youtube track url - cannot extract track id"


@unique
class InDatabaseStatus(Enum):
    ACCEPTED = "accepted"
    PENDING_APPROVAL = "pending"
    REJECTED = "rejected"


@unique
class Status(Enum):
    ACCEPTED = "accepted"
    PENDING_APPROVAL = "pending"
    REJECTED = "rejected"
    NOT_IN_LIBRARY = "NOT_IN_LIBRARY"

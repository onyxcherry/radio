import base64
import logging
import os
import sys
from datetime import time
from enum import Enum
from typing import Final, Optional
from zoneinfo import ZoneInfo

FORMATTER = logging.Formatter(
    "%(asctime)s.%(msecs)03d %(levelname)s %(module)s - " "%(funcName)s: %(message)s"
)


class MAX_TRACK_DURATION_SECONDS:
    _limit = 1200

    def __str__(self):
        return f"{self._limit}s"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger


def load_secret(secret_name: str) -> Optional[str]:
    secrets_dir = "/run/secrets"
    try:
        with open(os.path.join(secrets_dir, secret_name)) as secret_file:
            return secret_file.read().rstrip("\n")
    except IOError:
        return None


class TrackLibraryStatuses(Enum):
    ACCEPTED: Final = "zaakceptowane"
    PENDING_APPROVAL: Final = "oczekujace"
    REJECTED: Final = "odrzucone"
    NOT_IN_LIBRARY: Final = "NOT_IN_LIBRARY"


class Config(object):
    # settings = Dynaconf(
    #     envvar_prefix="RADIO",
    #     settings_files=["settings.toml", ".secrets.toml"],
    # )
    # settings.validators.validate()
    settings = {}
    SECRET_KEY = (
        load_secret("SECRET_KEY")
        or settings.get("SECRET_KEY")
        or base64.b64encode(os.urandom(32)).decode()
    )
    MONGO_PASSWORD: Final = load_secret("MONGODB_PASSWORD") or settings.get(
        "MONGODB_PASSWORD"
    )

    YOUTUBE_API_KEY: Final = (
        load_secret("YOUTUBE_API_KEY")
        or settings.get("YOUTUBE_API_KEY")
        or "testingpurposessecret"
    )
    CAPTCHA_SECRET_KEY: Final = load_secret("CAPTCHA_SECRET_KEY") or settings.get(
        "CAPTCHA_SECRET_KEY"
    )

    # CAPTCHA_SITE_KEY = settings.api.CAPTCHA_SITE_KEY
    # GSI_CLIENTS_IDS = settings.api.GSI_CLIENTS_IDS
    # GSI_ACCOUNTS_DOMAIN = settings.api.GSI_ACCOUNTS_DOMAIN

    # MAX_TRACKS_QUEUED_ONE_BREAK: Final = settings.constants.MAX_TRACKS_QUEUED_ONE_BREAK

    # MAX_TRACK_DURATION_SECONDS: Final = settings.constants.MAX_TRACK_DURATION_SECONDS

    # MONGO_HOST: Final = settings.database.HOST
    # MONGO_PORT: Final = settings.database.PORT
    # MONGO_USER: Final = settings.database.USER

    # DIRECTORY_DOWNLOAD_NAME: Final = settings.music.files_location.DOWNLOAD
    # DIRECTORY_READY_TO_PLAY_NAME: Final = settings.music.files_location.READY_TO_PLAY
    # HTTPS_ENABLED: Final = settings.security.HTTPS_ENABLED

    # MUSIC_HOST: Final = settings.music.HOST
    # MUSIC_PORT: Final = settings.music.PORT

    # NOTIFIER_HOST: Final = settings.notifier.HOST
    # NOTIFIER_PORT: Final = settings.notifier.PORT

    # RADIO_CHECK_PLAYBACK = settings.music.CHECK_PLAYBACK
    # TIME_SHIFT: Final = settings.music.TIME_SHIFT
    # OUR_TIMEZONE = ZoneInfo(settings.music.OUR_TIMEZONE)

    TRUTHY_VALUES: Final = frozenset(["y", "yes", "t", "true", "on", "1"])
    FALSY_VALUES: Final = frozenset(["n", "no", "f", "false", "off", "0"])

    YOUTUBE_API_URL: Final = "https://youtube.googleapis.com/youtube/v3/videos"
    VALID_TRACK_STATUSES: Final = frozenset(["zaakceptowane", "oczekujace"])
    ALL_TRACK_STATUSES = set(VALID_TRACK_STATUSES.copy())
    ALL_TRACK_STATUSES.add("odrzucone")

    # SESSION_COOKIE_SECURE = HTTPS_ENABLED or False
    SESSION_COOKIE_HTTPONLY: Final = True
    SESSION_COOKIE_SAMESITE: Final = "Strict"

    # key = starting time, value = duration
    breaks: Final = {
        time(8, 30): 10,
        time(9, 25): 10,
        time(10, 20): 10,
        time(11, 15): 15,
        time(12, 15): 10,
        time(13, 10): 10,
        time(14, 5): 10,
        time(15, 00): 10,
    }

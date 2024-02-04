class TrackIdentifierError(ValueError):
    pass


class TrackDurationExceeded(Exception):
    pass


class PlayingTimeError(ValueError):
    pass


class TrackAPIConfigurationError(Exception):
    pass


class TrackAPIMalformedResponse(Exception):
    pass


class TrackAPINoResults(Exception):
    pass


class TrackAPITimeout(Exception):
    pass


class TrackAPIConnectionError(Exception):
    pass


# class TrackLibraryUnknownStatus(Exception):
#     pass


# class TrackStatusUpdateError(Exception):
#     pass


# class TrackDownloadError(Exception):
#     pass

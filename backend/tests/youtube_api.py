from backend.src.track.domain.track import TrackId

_channel_info_data = {
    "YBcdt6DsLQA": {
        "channelId": "UC2XdaAVUannpujzv32jcouQ",
        "title": "The Beatles - Topic",
        "navigationEndpoint": {
            "clickTrackingParams": "CA0Q8DsiEwjB-pf8namEAxVuQ3oFHcE8CqM=",
            "commandMetadata": {
                "webCommandMetadata": {
                    "url": "/channel/UC2XdaAVUannpujzv32jcouQ",
                    "webPageType": "WEB_PAGE_TYPE_CHANNEL",
                    "rootVe": 3611,
                    "apiUrl": "/youtubei/v1/browse",
                }
            },
            "browseEndpoint": {
                "browseId": "UC2XdaAVUannpujzv32jcouQ",
                "canonicalBaseUrl": "/channel/UC2XdaAVUannpujzv32jcouQ",
            },
        },
        "avatar": {"thumbnails": []},
        "banner": {"thumbnails": []},
        "headerLinks": {"channelHeaderLinksViewModel": {"firstLink": {}}},
        "subscribeButton": {},
        "tvBanner": {},
        "mobileBanner": {},
        "trackingParams": "...",
        "style": "C4_TABBED_HEADER_RENDERER_STYLE_PAGE_HEADER",
        "videosCountText": {"runs": [{"text": "2.2K"}, {"text": " videos"}]},
        "tagline": {},
    }
}
_snippet_data = {
    "ZDZiXmCl4pk": {
        "publishedAt": "2024-01-19T17:00:08Z",
        "channelId": "UCYpVqLSvfseUqb2URAkexlw",
        "title": "Kygo, Ava Max - Whatever (Official Video)",
        "description": "...",
        "thumbnails": {},
        "channelTitle": "KygoOfficialVEVO",
        "tags": ["..."],
        "categoryId": "10",
        "liveBroadcastContent": "none",
        "localized": {
            "title": "Kygo, Ava Max - Whatever (Official Video)",
            "description": "...",
        },
    },
    "YBcdt6DsLQA": {
        "publishedAt": "2018-06-17T11:18:05Z",
        "channelId": "UC2XdaAVUannpujzv32jcouQ",
        "title": "In My Life (Remastered 2009)",
        "description": "...",
        "thumbnails": {},
        "channelTitle": "The Beatles - Topic",
        "tags": ["..."],
        "categoryId": "10",
        "liveBroadcastContent": "none",
        "localized": {
            "title": "In My Life (Remastered 2009)",
            "description": "...",
        },
    },
}

_content_details_data = {
    "ZDZiXmCl4pk": {
        "duration": "PT3M9S",
        "dimension": "2d",
        "definition": "hd",
        "caption": "true",
        "licensedContent": True,
        "regionRestriction": {"blocked": ["..."]},
        "contentRating": {},
        "projection": "rectangular",
    },
    "YBcdt6DsLQA": {
        "duration": "PT2M27S",
        "dimension": "2d",
        "definition": "hd",
        "caption": "false",
        "licensedContent": True,
        "regionRestriction": {"allowed": ["..."]},
        "contentRating": {},
        "projection": "rectangular",
    },
}


class YoutubeAPIInterface:
    @staticmethod
    def get_api_part(track_id: TrackId, part: str) -> dict:
        if part == "snippet":
            return _snippet_data[track_id]
        elif part == "contentDetails":
            return _content_details_data[track_id]
        else:
            raise KeyError

    @staticmethod
    def get_channel_info(channel_id: str) -> dict:
        return _channel_info_data[channel_id]

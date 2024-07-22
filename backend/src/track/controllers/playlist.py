from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse
from kink import di

from track.application.playlist import Playlist
from .json_encoder import MyJSONEncoder
from track.domain.breaks import Breaks, PlayingTime
from track.application.requests_service import RequestResult, RequestsService
from track.domain.provided import Identifier, ProviderName, TrackProvidedIdentity
from track.domain.entities import TrackQueued
from building_blocks.errors import APIErrorMessage

router = APIRouter()

json_encoder = MyJSONEncoder()


@router.get(
    "/playlist/",
    response_model=list[TrackQueued],
    responses={
        400: {"model": APIErrorMessage},
        404: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["playlist"],
)
async def list_all(
    date_: date = Query(..., description="Playing date", alias="date"),
    break_: Optional[Breaks] = Query(
        None, description="Playing break number", alias="break"
    ),
    played: Optional[bool] = Query(None, description="If played"),
    waiting: Optional[bool] = Query(None, description="If waiting"),
    playlist: Playlist = Depends(lambda: di[Playlist]),
) -> JSONResponse:
    result = playlist.get_all(date_, break_, played, waiting)
    content = json_encoder.default(result)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.put(
    "/playlist/",
    response_model=RequestResult,
    responses={
        400: {"model": APIErrorMessage},
        404: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["playlist"],
)
async def add(
    identifier: Identifier,
    provider: ProviderName,
    date_: date = Query(..., description="Playing date", alias="date"),
    break_: Breaks = Query(..., description="Playing break number", alias="break"),
    rs: RequestsService = Depends(lambda: di[RequestsService]),
) -> JSONResponse:
    identity = TrackProvidedIdentity(identifier, provider)
    when = PlayingTime(date_, break_)
    result = rs.request_on(identity, when)
    content = json_encoder.default(result)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.delete(
    "/playlist/",
    response_model=TrackQueued | None,
    responses={
        400: {"model": APIErrorMessage},
        404: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["playlist"],
)
async def delete(
    track: TrackQueued,
    playlist: Playlist = Depends(lambda: di[Playlist]),
) -> JSONResponse:
    result = playlist.delete(track)
    content = json_encoder.default(result)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)

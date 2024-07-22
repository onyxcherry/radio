from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse
from kink import di

from .json_encoder import MyJSONEncoder
from track.application.requests_service import (
    AddToLibraryStatus,
    RequestsService,
)
from track.domain.provided import TrackProvidedIdentity
from track.application.library import Library
from track.domain.entities import Status, TrackInLibrary
from building_blocks.errors import APIErrorMessage

router = APIRouter()

json_encoder = MyJSONEncoder()


@router.get(
    "/library/",
    response_model=TrackInLibrary,
    responses={
        400: {"model": APIErrorMessage},
        404: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["library"],
)
async def filter_by_statuses(
    statuses: Optional[list[Status]] = Query(
        list(), description="Comma-separated list of statuses"
    ),
    library: Library = Depends(lambda: di[Library]),
) -> JSONResponse:
    result = library.filter_by_statuses(statuses or [])
    content = json_encoder.default(result)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.post(
    "/library/",
    response_model=AddToLibraryStatus,
    responses={
        400: {"model": APIErrorMessage},
        404: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["library"],
)
def add(
    identity: TrackProvidedIdentity,
    rs: RequestsService = Depends(lambda: di[RequestsService]),
):
    result = rs.add_to_library(identity)
    content = json_encoder.default(result)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.post(
    "/library/accept",
    response_model=TrackInLibrary,
    responses={
        400: {"model": APIErrorMessage},
        404: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["library"],
)
def accept(
    identity: TrackProvidedIdentity,
    rs: RequestsService = Depends(lambda: di[RequestsService]),
):
    result = rs.accept(identity)
    content = json_encoder.default(result)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.post(
    "/library/reject",
    response_model=TrackInLibrary,
    responses={
        400: {"model": APIErrorMessage},
        404: {"model": APIErrorMessage},
        500: {"model": APIErrorMessage},
    },
    tags=["library"],
)
def reject(
    identity: TrackProvidedIdentity,
    rs: RequestsService = Depends(lambda: di[RequestsService]),
):
    result = rs.reject(identity)
    content = MyJSONEncoder().default(result)
    return JSONResponse(content=content, status_code=status.HTTP_200_OK)

from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from boostrap import boostrap_di
from building_blocks.errors import (
    APIErrorMessage,
    DomainError,
    RepositoryError,
    ResourceNotFound,
)
from track.controllers.library import router as library_router
from track.controllers.playlist import router as playlist_router

boostrap_di()


app = FastAPI()
app.include_router(library_router)
app.include_router(playlist_router)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    error_msg = APIErrorMessage(type=exc.__class__.__name__, message=f"Oops! {exc}")
    return JSONResponse(
        status_code=400,
        content=error_msg.__dict__,
    )


@app.exception_handler(ResourceNotFound)
async def resource_not_found_handler(
    request: Request, exc: ResourceNotFound
) -> JSONResponse:
    error_msg = APIErrorMessage(type=exc.__class__.__name__, message=str(exc))
    return JSONResponse(status_code=404, content=error_msg.__dict__)


@app.exception_handler(RepositoryError)
async def repository_error_handler(
    request: Request, exc: RepositoryError
) -> JSONResponse:
    error_msg = APIErrorMessage(
        type=exc.__class__.__name__,
        message="Oops! Something went wrong, please try again later...",
    )
    return JSONResponse(
        status_code=500,
        content=error_msg.__dict__,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal Server Error"},
    )


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema  # type: ignore

    openapi_schema = get_openapi(
        title="radio-backend",
        version="0.0.1",
        description="Radio",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema

    return app.openapi_schema  # type: ignore


app.openapi = custom_openapi  # type: ignore

if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8000, reload=True)

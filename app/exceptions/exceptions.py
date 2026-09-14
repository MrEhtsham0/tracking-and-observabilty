from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from opentelemetry import trace
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorResponse(BaseModel):
    status_code: int
    detail: Any


class AppException(Exception):
    """Base application exception with status code and detail."""

    def __init__(self, status_code: int = 400, detail: Any = "An error occurred"):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))


def _record_span_error(exc: Exception, status_code: int):
    """Helper to record exception and status on current OpenTelemetry span if active."""
    span = trace.get_current_span()
    if span and span.is_recording():
        span.record_exception(exc)
        span.set_status(trace.StatusCode.ERROR, str(exc))
        span.set_attribute("http.status_code", status_code)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers on the FastAPI application.
    Captures exact status code, error details, and records them to OpenTelemetry traces.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        _record_span_error(exc, exc.status_code)
        response_data = ErrorResponse(
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data.model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        _record_span_error(exc, exc.status_code)
        response_data = ErrorResponse(
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data.model_dump(),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        _record_span_error(exc, status_code)
        response_data = ErrorResponse(
            status_code=status_code,
            detail=exc.errors(),
        )
        return JSONResponse(
            status_code=status_code,
            content=response_data.model_dump(),
        )

    @app.exception_handler(500)
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if isinstance(exc, Exception):
            _record_span_error(exc, status_code)
            detail = str(exc) if str(exc) else "Internal Server Error"
        else:
            detail = "Internal Server Error"

        response_data = ErrorResponse(
            status_code=status_code,
            detail=detail,
        )
        return JSONResponse(
            status_code=status_code,
            content=response_data.model_dump(),
        )
    
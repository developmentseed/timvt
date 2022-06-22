"""timvt.errors: Error classes."""

import logging
from typing import Callable, Dict, Type

from fastapi import FastAPI

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class TiMVTError(Exception):
    """Base exception class."""


class TableNotFound(TiMVTError):
    """Invalid table name."""


class MissingEPSGCode(TiMVTError):
    """No EPSG code available for TMS's CRS."""


class MissingGeometryColumn(TiMVTError):
    """Table has no geometry column."""


class InvalidGeometryColumnName(TiMVTError):
    """Invalid geometry column name."""


DEFAULT_STATUS_CODES = {
    TableNotFound: status.HTTP_404_NOT_FOUND,
    MissingEPSGCode: status.HTTP_500_INTERNAL_SERVER_ERROR,
    MissingGeometryColumn: status.HTTP_500_INTERNAL_SERVER_ERROR,
    InvalidGeometryColumnName: status.HTTP_404_NOT_FOUND,
    Exception: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def exception_handler_factory(status_code: int) -> Callable:
    """
    Create a FastAPI exception handler from a status code.
    """

    def handler(request: Request, exc: Exception):
        logger.error(exc, exc_info=True)
        return JSONResponse(content={"detail": str(exc)}, status_code=status_code)

    return handler


def add_exception_handlers(
    app: FastAPI, status_codes: Dict[Type[Exception], int]
) -> None:
    """
    Add exception handlers to the FastAPI app.
    """
    for (exc, code) in status_codes.items():
        app.add_exception_handler(exc, exception_handler_factory(code))

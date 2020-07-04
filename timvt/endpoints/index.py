"""TiVTiler.index: Index endpoint."""

from typing import List

from ..models.metadata import TableMetadata

from fastapi import APIRouter, Request

router = APIRouter()


@router.get(
    "/index",
    response_model=List[TableMetadata],
    tags=["Database"],
    description="Return available tables.",
    deprecated=True,
)
@router.get(
    "/index.json",
    response_model=List[TableMetadata],
    tags=["Database"],
    description="Return available tables.",
)
async def display_index(request: Request):
    """Return JSON with available table metadata. """
    return request.app.state.Catalog

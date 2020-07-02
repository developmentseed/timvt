"""TiVTiler Metadata models."""

from typing import Dict

from pydantic import BaseModel, Field


class TableMetadata(BaseModel):
    """Table Metadata."""

    table: str
    dbschema: str = Field(..., alias="schema")
    columns: Dict[str, str]
    geometry_column: str

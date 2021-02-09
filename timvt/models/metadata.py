"""timvt Metadata models."""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class TableMetadata(BaseModel):
    """Table Metadata."""

    id: str
    dbschema: str = Field(..., alias="schema")
    table: str
    geometry_column: str
    srid: int
    geometry_type: str
    properties: Dict[str, str]
    bounds: str
    link: Optional[str]

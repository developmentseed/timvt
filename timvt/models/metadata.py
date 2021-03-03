"""timvt Metadata models."""

from typing import Dict, Optional, Tuple

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
    bounds: Tuple[float, float, float, float]
    link: Optional[str]

"""timvt Metadata models."""

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, root_validator

from timvt.settings import DEFAULT_MAXZOOM, DEFAULT_MINZOOM


class TableMetadata(BaseModel):
    """Table Metadata."""

    id: str
    dbschema: str = Field(..., alias="schema")
    table: str
    geometry_type: str
    geometry_column: str
    bounds: List[float] = [-180, -90, 180, 90]
    center: Optional[Tuple[float, float, int]]
    tileurl: Optional[str]
    properties: Dict[str, str]
    minzoom: int = DEFAULT_MINZOOM
    maxzoom: int = DEFAULT_MAXZOOM

    @root_validator
    def compute_center(cls, values):
        """Compute center if it does not exist."""
        bounds = values["bounds"]
        if not values.get("center"):
            values["center"] = (
                (bounds[0] + bounds[2]) / 2,
                (bounds[1] + bounds[3]) / 2,
                values["minzoom"],
            )
        return values

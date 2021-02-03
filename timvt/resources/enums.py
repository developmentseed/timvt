"""timvt.resources.enums."""

from enum import Enum


class VectorType(str, Enum):
    """Vector Type Enums."""

    pbf = "pbf"
    mvt = "mvt"


class MimeTypes(str, Enum):
    """Responses MineTypes."""

    xml = "application/xml"
    json = "application/json"
    geojson = "application/geo+json"
    html = "text/html"
    text = "text/plain"
    pbf = "application/x-protobuf"
    mvt = "application/x-protobuf"

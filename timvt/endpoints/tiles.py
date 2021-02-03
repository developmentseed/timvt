"""timvt.endpoints.tiles: Vector Tiles endpoint."""

from timvt.endpoints.factory import VectorTilerFactory

router = VectorTilerFactory().router  # noqa

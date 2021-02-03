"""timvt.endpoint.tms: TileMatrixSet routes."""


from timvt.dependencies import TileMatrixSetNames, TileMatrixSetParams
from timvt.endpoints.factory import TMSFactory

tms = TMSFactory(supported_tms=TileMatrixSetNames, tms_dependency=TileMatrixSetParams)
router = tms.router  # noqa

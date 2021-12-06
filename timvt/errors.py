"""TiVTiler.errors: Error classes."""


class TilerError(Exception):
    """Base exception class."""


class TableNotFound(TilerError):
    """Invalid table name."""


class MissingEPSGCode(TilerError):
    """No EPSG code available for TMS's CRS."""

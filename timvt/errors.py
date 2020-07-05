"""TiVTiler.errors: Error classes."""


class TilerError(Exception):
    """Base exception class."""


class TableNotFound(TilerError):
    """Invalid table name."""

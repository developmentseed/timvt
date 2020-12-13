"""TiVTiler.db.functions: custom functions"""
import abc
from dataclasses import dataclass
from typing import ClassVar, Dict

from morecantile.models import BoundingBox


@dataclass  # type: ignore
class Function(abc.ABC):
    """named function for fetching vector tiles from the backend"""

    name: str

    @abc.abstractmethod
    async def __call__(self, bbox: BoundingBox, **kwargs) -> bytes:
        """call the function"""
        ...


@dataclass
class SqlFunction(Function):
    """postgres function"""

    sql: str

    async def __call__(self, bbox: BoundingBox, **kwargs):
        """call the function"""
        ...


@dataclass
class Registry:
    """function registry"""

    funcs: ClassVar[Dict[str, Function]] = {}

    @classmethod
    def get(cls, key: str):
        """lookup function by name"""
        return cls.funcs.get(key)

    @classmethod
    def register(cls, *args: Function):
        """register function(s)"""
        for func in args:
            cls.funcs[func.name] = func


register = Registry.register

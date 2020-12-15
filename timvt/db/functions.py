"""TiVTiler.db.functions: custom functions"""
import abc
from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from buildpg.asyncpg import BuildPgPool
from morecantile.models import BoundingBox


@dataclass  # type: ignore
class Function(abc.ABC):
    """named function for fetching vector tiles from the backend"""

    name: str

    @abc.abstractmethod
    async def __call__(self, bbox: BoundingBox, resource: Any, **kwargs) -> bytes:
        """call the function"""
        ...


@dataclass
class SqlFunction(Function):
    """postgres function"""

    sql: str

    async def __call__(self, bbox: BoundingBox, resource: BuildPgPool, **kwargs):
        """call the function"""
        async with resource.acquire() as conn:
            content = await conn.fetchval_b(
                self.sql,
                xmin=bbox.left,
                ymin=bbox.bottom,
                xmax=bbox.right,
                ymax=bbox.top,
                **kwargs
            )
        return content


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

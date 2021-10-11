"""TiVTiler.functions: custom functions"""

from dataclasses import dataclass
from typing import ClassVar, Dict

from timvt.layer import Function


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
            cls.funcs[func.id] = func


registry = Registry()

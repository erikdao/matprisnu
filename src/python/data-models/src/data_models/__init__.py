from importlib.metadata import version

from .scrappers import (AxfoodAPIProduct, CoopAPICategory, IcaAPICategory,
                        IcaAPIStore)

__version__ = version("data-models")

__all__ = [
    "CoopAPICategory",
    "AxfoodAPIProduct",
    "IcaAPIStore",
    "IcaAPICategory",
]

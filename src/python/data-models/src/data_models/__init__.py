from .scrappers import (
    AxfoodAPICategory,
    AxfoodAPIProduct,
    AxfoodAPIStore,
    CoopAPICategory,
    CoopAPIStore,
    IcaAPICategory,
    IcaAPIStore,
)

__version__ = "0.1.0"

__all__ = [
    "CoopAPIStore",
    "CoopAPICategory",
    "AxfoodAPICategory",
    "AxfoodAPIProduct",
    "AxfoodAPIStore",
    "IcaAPIStore",
    "IcaAPICategory",
]

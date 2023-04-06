"""Data models used in scrappers."""
from typing import Any, List, Optional

from pydantic import BaseModel


class CoopAPICategory(BaseModel):
    """Category model for Coop API."""

    id: int
    name: str
    level: int
    escapedName: str
    hasChildren: bool = False
    parent: Optional[int]

    def __str__(self) -> str:
        return f"CoopAPICategory(id={self.id}, name={self.name})"


class AxfoodAPIProduct(BaseModel):
    """Product model for Axfood API (i.e., Hemkop and Willys)."""

    code: str
    name: str
    price_value: float

    def __str__(self) -> str:
        return f"AxfoodAPIProduct(code={self.code}, name={self.name})"


class AxfoodAPICategory(BaseModel):
    """Category model for Axfood API (i.e., Hemkop and Willys)."""

    id: str
    category: str
    title: str
    url: Optional[str] = None
    valid: Optional[bool] = True
    children: Optional[List["AxfoodAPICategory"]] = []

    def __str__(self) -> str:
        return f"AxfoodAPICategory(id={self.id}, url={self.url})"


class IcaAPIStore(BaseModel):
    """Store model for ICA API."""

    storeId: str
    storeName: str
    profile: str
    accountNumber: str
    phoneNumber: Optional[str] = None
    emailAddress: Optional[str] = None
    onlinePlatform: Optional[str] = None
    onlineUrl: Optional[str] = None
    distanceInMeters: Optional[float] = None

    def __str__(self) -> str:
        return f"IcaAPIStore(storeId={self.storeId}, storeName={self.storeName})"


class IcaAPICategory(BaseModel):
    """Category model for ICA API."""

    id: str
    name: str
    retailerId: Optional[str] = None
    fullURLPath: Optional[str] = None
    children: Optional[List[str]] = []
    products: Optional[List[Any]] = None

    def __str__(self) -> str:
        return f"IcaAPICategory(id={self.id}, name={self.name})"

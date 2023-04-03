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


class AxfoodAPIProduct(BaseModel):
    """Product model for Axfood API (i.e., Hemkop and Willys)."""

    code: str
    name: str
    price_value: float


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


class IcaAPICategory(BaseModel):
    """Category model for ICA API."""

    id: str
    name: str
    retailerId: Optional[str] = None
    fullURLPath: Optional[str] = None
    children: Optional[List[str]] = []
    products: Optional[List[Any]] = None

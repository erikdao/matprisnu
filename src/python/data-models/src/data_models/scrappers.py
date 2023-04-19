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


class CoopAPIStore(BaseModel):
    """Store model for Coop API."""

    storeId: int
    ledgerAccountNumber: str
    name: str
    address: str
    phone: Optional[str]
    openingHoursToday: Optional[str]
    latitude: float
    longitude: float
    url: Optional[str]
    city: Optional[str]
    postalCode: Optional[str]

    def __str__(self) -> str:
        return f"CoopAPIStore(storeId={self.storeId}, name={self.name})"


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


class AxfoodAPIGeoPoint(BaseModel):
    """GeoPoint model for Axfood API (i.e., Hemkop and Willys)."""

    latitude: float
    longitude: float

    def __str__(self) -> str:
        return f"AxfoodAPIGeoPoint(lat={self.lat}, lon={self.lon})"


class AxfoodAPICountry(BaseModel):
    """Country model for Axfood API (i.e., Hemkop and Willys)."""

    name: str
    isocode: str

    def __str__(self) -> str:
        return f"AxfoodAPICountry(isocode={self.isocode}, name={self.name})"


class AxfoodAPIAddress(BaseModel):
    """Address model for Axfood API (i.e., Hemkop and Willys)."""

    id: str
    title: Optional[str] = None
    titleCode: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    companyName: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    town: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    postcalCode: Optional[str] = None
    phone: Optional[str] = None
    cellPhone: Optional[str] = None
    email: Optional[str] = None
    country: Optional[AxfoodAPICountry] = None
    shippingAddress: Optional[bool] = False
    billingAddress: Optional[bool] = False
    defaultAddress: Optional[bool] = False
    visibleInAddressBook: Optional[bool] = False
    formattedAddress: Optional[str] = None
    longitiude: Optional[float] = None
    latitude: Optional[float] = None
    appartment: Optional[str] = None
    doorCode: Optional[str] = None
    customerComment: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"AxfoodAPIAddress(id={self.id}, formattedAddress={self.formattedAddress})"
        )


class AxfoodAPIStore(BaseModel):
    """Store model for Axfood API (i.e., Hemkop and Willys)."""

    storeId: str
    name: str
    externalPickupLocation: Optional[bool] = False
    deliveryCost: Optional[str] = None
    geoPoint: AxfoodAPIGeoPoint
    storeChangeAllowed: Optional[bool] = False
    openingHours: Optional[List[str]] = []
    willysHemma: Optional[bool] = False
    clickAndCollect: Optional[bool] = False
    extraPickUpInformation: Optional[str] = None
    pickingCostForCollect: Optional[str] = None
    b2bPickingCostForDelivery: Optional[str] = None
    pickingCostForDelivery: Optional[str] = None
    b2bDeliveryCost: Optional[str] = None
    customerServicePhone: Optional[str] = None
    openingHoursMessageKey: Optional[str] = None
    onlineStore: Optional[bool] = False
    pickingCostForCollectPlusPickupCost: Optional[str] = None
    b2bPickingCostForCollectPlusPickupCost: Optional[str] = None
    pickingCostForDeliveryPlusDeliveryCost: Optional[str] = None
    b2bPickingCostForDeliveryPlusDeliveryCost: Optional[str] = None
    openingStoreMessageValue: Optional[str] = None
    specialOpeningHours: Optional[List[str]] = []
    b2BClickAndCollect: Optional[bool] = False
    franchiseStore: Optional[bool] = False
    freeDeliveryThresholdFormatted: Optional[str] = None
    b2bFreeDeliveryThresholdFormatted: Optional[str] = None
    pickupInStoreCost: Optional[str] = None
    b2bPickupInStoreCost: Optional[str] = None
    customerServiceEmail: Optional[str] = None
    flyerURL: Optional[str] = None
    activelySelected: Optional[bool] = False
    freePickingCostThresholdForCollectFormatted: Optional[str] = None
    freePickingCostThresholdForDeliveryFormatted: Optional[str] = None
    freeB2BPickingCostThresholdForCollectFormatted: Optional[str] = None
    freeB2BPickingCostThresholdForDeliveryFormatted: Optional[str] = None
    external: Optional[bool] = False
    open: Optional[bool] = False
    address: Optional[AxfoodAPIAddress] = None

    def __str__(self) -> str:
        return f"AxfoodAPIStore(storeId={self.storeId}, name={self.name})"


class IcaApiAddressCoordinates(BaseModel):
    """Address coordinates model for ICA API."""

    coordinateX: Optional[str] = None
    coordinateY: Optional[str] = None

    def __str__(self) -> str:
        return f"IcaApiAddressCoordinates(coordinateX={self.coordinateX}, coordinateY={self.coordinateY})"


class IcaApiAddress(BaseModel):
    """Address model for ICA API."""

    street: Optional[str] = None
    city: Optional[str] = None
    postalCode: Optional[str] = None
    county: Optional[str] = None
    municipality: Optional[str] = None
    urbanArea: Optional[str] = None
    coordinates: Optional[IcaApiAddressCoordinates] = None

    def __str__(self) -> str:
        return f"IcaApiAddress(postalCode={self.postalCode}, city={self.city})"


class IcaApiStoreMdsaFilters(BaseModel):
    """Store MDSA filters model for ICA API."""

    district: Optional[str] = None
    informations: Optional[List[str]] = []
    profile: str
    services: Optional[List[str]] = []
    urbanArea: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"IcaApiStoreMdsaFilters(district={self.district}, profile={self.profile})"
        )


class IcaApiStoreUrl(BaseModel):
    """Store URL model for ICA API."""

    url: str
    code: str
    urlDescription: str

    def __str__(self) -> str:
        return f"IcaApiStoreUrl(url={self.url})"


class IcaAPIStore(BaseModel):
    """Store model for ICA API without the `openingHours` attribute."""

    storeId: str
    storeName: str
    profile: str
    accountNumber: str
    phoneNumber: Optional[str] = None
    emailAddress: Optional[str] = None
    onlinePlatform: Optional[str] = None
    onlineUrl: Optional[str] = None
    distanceInMeters: Optional[float] = None
    services: Optional[List[str]] = []
    address: Optional[IcaApiAddress] = None
    mdsaFilters: Optional[IcaApiStoreMdsaFilters] = None
    urls: Optional[List[IcaApiStoreUrl]] = []

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

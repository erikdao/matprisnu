"""Data models for ingestion."""
from typing import Optional

from pydantic import BaseModel


class CoopPriceData(BaseModel):
    """Price data model for Coop."""

    b2cPrice: float
    b2bPrice: float


class CoopVat(BaseModel):
    """VAT model for Coop."""

    code: str
    type: str
    value: float


class CoopOnlinePromotion(BaseModel):
    """Online promotion model for Coop."""

    id: str
    price: float
    type: str
    startDate: Optional[str]
    endDate: Optional[str]
    price: Optional[float]
    priceData: Optional[CoopPriceData]
    message: Optional[str]
    numberOfProducts: Optional[int]
    medMeraRabatt: Optional[bool]
    priority: Optional[int]


class CoopCodeValue(BaseModel):
    """Code value model for Coop."""

    code: str
    value: str


class CoopAnimalFoodData(BaseModel):
    """Animal food data model for Coop."""

    feedAdditiveStatement: Optional[str]
    feedAnalyticalConstituentsStatement: Optional[str]
    feedCompositionStatement: Optional[str]
    feedingInstructions: Optional[str]
    feedType: Optional[str]
    feedLifeStage: Optional[str]
    targetedConsumptionBy: Optional[CoopCodeValue]


class CoopNutrientBasis(BaseModel):
    quantity: float


class CoopProduct(BaseModel):
    """Product model for Coop."""

    id: str
    type: str
    ean: str
    description: Optional[str]
    manufacturerName: Optional[str]
    imageUrl: Optional[str]
    packageSize: Optional[float]
    packageSizeInformation: Optional[str]
    packageSizeUnit: Optional[str]
    salesPrice: Optional[float]
    salesPriceData: Optional[CoopPriceData]
    piecePrice: Optional[float]
    piecePriceData: Optional[CoopPriceData]
    salesUnit: Optional[str]
    comparativePriceText: Optional[str]
    comparativePrice: Optional[float]
    comparativePriceData: Optional[CoopPriceData]
    articleSold: Optional[bool]
    deposit: Optional[float]
    depositData: Optional[CoopPriceData]
    vat: Optional[CoopVat]
    fromSweden: Optional[bool]
    availableOnline: Optional[bool]
    onlinePromotion: Optional[CoopOnlinePromotion]
    animalFoodData: Optional[CoopAnimalFoodData]
    nutrientBasis: Optional[CoopNutrientBasis]

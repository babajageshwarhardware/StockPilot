from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class Unit(str, Enum):
    PIECE = "piece"
    KG = "kg"
    LITER = "liter"
    METER = "meter"
    BOX = "box"
    DOZEN = "dozen"

class Pricing(BaseModel):
    purchasePrice: float = Field(..., ge=0)
    sellingPrice: float = Field(..., ge=0)
    mrp: float = Field(..., ge=0)
    discount: float = Field(default=0, ge=0, le=100)
    taxRate: float = Field(default=0, ge=0, le=100)

class Stock(BaseModel):
    quantity: float = Field(default=0, ge=0)
    reorderPoint: float = Field(default=0, ge=0)
    warehouse: Optional[str] = None

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=50)
    barcode: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)
    category: str
    brand: Optional[str] = None
    unit: Unit = Unit.PIECE
    pricing: Pricing
    stock: Stock
    supplier: Optional[str] = None
    isActive: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    brand: Optional[str] = None
    unit: Optional[Unit] = None
    pricing: Optional[Pricing] = None
    stock: Optional[Stock] = None
    supplier: Optional[str] = None
    isActive: Optional[bool] = None

class ProductResponse(ProductBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    createdBy: str
    createdAt: datetime
    updatedAt: datetime
    profitMargin: Optional[float] = None
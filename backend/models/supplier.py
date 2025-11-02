from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class PaymentTerms(str, Enum):
    IMMEDIATE = "immediate"
    NET15 = "net15"
    NET30 = "net30"
    NET60 = "net60"

class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: str = Field(..., pattern=r"^[0-9]{10}$")
    gstNumber: Optional[str] = None
    address: Optional[Address] = None
    paymentTerms: PaymentTerms = PaymentTerms.NET30
    outstandingBalance: float = Field(default=0, ge=0)
    rating: Optional[float] = Field(None, ge=1, le=5)
    isActive: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^[0-9]{10}$")
    gstNumber: Optional[str] = None
    address: Optional[Address] = None
    paymentTerms: Optional[PaymentTerms] = None
    rating: Optional[float] = Field(None, ge=1, le=5)
    isActive: Optional[bool] = None

class SupplierResponse(SupplierBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    createdAt: datetime
    updatedAt: datetime
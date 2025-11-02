from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: str = Field(..., pattern=r"^[0-9]{10}$")
    gstNumber: Optional[str] = None
    address: Optional[Address] = None
    loyaltyPoints: float = Field(default=0, ge=0)
    creditLimit: float = Field(default=0, ge=0)
    outstandingBalance: float = Field(default=0, ge=0)
    isActive: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^[0-9]{10}$")
    gstNumber: Optional[str] = None
    address: Optional[Address] = None
    creditLimit: Optional[float] = Field(None, ge=0)
    isActive: Optional[bool] = None

class CustomerResponse(CustomerBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    createdAt: datetime
    updatedAt: datetime
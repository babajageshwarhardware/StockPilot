from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PaymentMode(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    CREDIT = "credit"

class PaymentStatus(str, Enum):
    PAID = "paid"
    PARTIAL = "partial"
    PENDING = "pending"
    REFUNDED = "refunded"

class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

class SaleItem(BaseModel):
    productId: str
    productName: str
    sku: str
    quantity: float = Field(..., gt=0)
    unitPrice: float = Field(..., ge=0)
    discount: float = Field(default=0, ge=0)
    discountType: DiscountType = DiscountType.FIXED
    taxRate: float = Field(default=0, ge=0, le=100)
    taxAmount: float = Field(default=0, ge=0)
    lineTotal: float = Field(..., ge=0)

class SaleBase(BaseModel):
    customerId: Optional[str] = None
    customerName: Optional[str] = None
    customerPhone: Optional[str] = None
    items: List[SaleItem] = Field(..., min_length=1)
    subtotal: float = Field(..., ge=0)
    discountAmount: float = Field(default=0, ge=0)
    discountType: DiscountType = DiscountType.FIXED
    taxAmount: float = Field(default=0, ge=0)
    total: float = Field(..., ge=0)
    amountPaid: float = Field(default=0, ge=0)
    paymentMode: PaymentMode
    paymentStatus: PaymentStatus
    notes: Optional[str] = Field(None, max_length=500)

class SaleCreate(SaleBase):
    pass

class SaleUpdate(BaseModel):
    paymentStatus: Optional[PaymentStatus] = None
    amountPaid: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class SaleResponse(SaleBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    invoiceNumber: str
    saleDate: datetime
    createdBy: str
    createdAt: datetime
    updatedAt: datetime

class ReturnItem(BaseModel):
    productId: str
    quantity: float = Field(..., gt=0)
    reason: Optional[str] = None

class SaleReturn(BaseModel):
    items: List[ReturnItem] = Field(..., min_length=1)
    refundAmount: float = Field(..., ge=0)
    refundMode: PaymentMode
    reason: Optional[str] = Field(None, max_length=500)

class SaleStats(BaseModel):
    totalSales: float
    totalTransactions: int
    averageOrderValue: float
    todaySales: float
    weekSales: float
    monthSales: float
    topProducts: List[dict]
    recentSales: List[SaleResponse]

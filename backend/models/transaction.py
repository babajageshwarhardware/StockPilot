from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    SALE = "sale"
    RETURN = "return"
    REFUND = "refund"
    PURCHASE = "purchase"
    EXPENSE = "expense"

class TransactionStatus(str, Enum):
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransactionBase(BaseModel):
    referenceId: str  # saleId, purchaseId, etc.
    referenceType: TransactionType
    amount: float = Field(..., ge=0)
    paymentMode: str
    description: Optional[str] = Field(None, max_length=500)
    status: TransactionStatus = TransactionStatus.SUCCESS

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    transactionDate: datetime
    createdBy: Optional[str] = None
    createdAt: datetime

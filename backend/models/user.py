from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SALES_EXECUTIVE = "sales_executive"
    ACCOUNTANT = "accountant"

class Permission(str, Enum):
    VIEW_SALES = "view_sales"
    CREATE_SALES = "create_sales"
    EDIT_SALES = "edit_sales"
    DELETE_SALES = "delete_sales"
    VIEW_PRODUCTS = "view_products"
    CREATE_PRODUCTS = "create_products"
    EDIT_PRODUCTS = "edit_products"
    DELETE_PRODUCTS = "delete_products"
    VIEW_PURCHASES = "view_purchases"
    CREATE_PURCHASES = "create_purchases"
    EDIT_PURCHASES = "edit_purchases"
    DELETE_PURCHASES = "delete_purchases"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_REPORTS = "view_reports"
    MANAGE_USERS = "manage_users"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    role: UserRole
    phone: Optional[str] = Field(None, pattern=r"^[0-9]{10}$")
    permissions: List[Permission] = []
    isActive: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^[0-9]{10}$")
    isActive: Optional[bool] = None
    permissions: Optional[List[Permission]] = None

class UserInDB(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    hashed_password: str
    lastLogin: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

class UserResponse(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    lastLogin: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

class ChangePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str = Field(..., min_length=8)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str
    email: str
    role: str
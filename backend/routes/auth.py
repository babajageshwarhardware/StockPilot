from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserCreate, UserResponse, UserRole, Permission, Token, ChangePasswordRequest
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from middleware.auth import get_current_user
import uuid
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    refresh_token: str
    user: UserResponse

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Set default permissions based on role
    permissions_map = {
        UserRole.ADMIN: [p.value for p in Permission],
        UserRole.MANAGER: [p.value for p in Permission if p != Permission.MANAGE_USERS],
        UserRole.ACCOUNTANT: [Permission.VIEW_SALES.value, Permission.VIEW_PRODUCTS.value, 
                             Permission.VIEW_PURCHASES.value, Permission.VIEW_ANALYTICS.value, 
                             Permission.VIEW_REPORTS.value],
        UserRole.SALES_EXECUTIVE: [Permission.VIEW_SALES.value, Permission.CREATE_SALES.value,
                                   Permission.VIEW_PRODUCTS.value]
    }
    
    if not user_data.permissions:
        user_data.permissions = permissions_map.get(user_data.role, [])
    
    # Create user document
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    user_doc = {
        "id": user_id,
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "role": user_data.role.value,
        "phone": user_data.phone,
        "permissions": user_data.permissions,
        "isActive": True,
        "lastLogin": None,
        "createdAt": now.isoformat(),
        "updatedAt": now.isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Return user without password
    user_doc.pop("hashed_password")
    user_doc.pop("_id")
    return user_doc

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login user and return JWT tokens"""
    # Find user by email
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"lastLogin": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create tokens
    token_data = {
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Prepare user response
    user.pop("hashed_password")
    user.pop("_id")
    user["lastLogin"] = datetime.now(timezone.utc).isoformat()
    
    return {
        "success": True,
        "token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    # Get user with password
    user = await db.users.find_one({"id": current_user["id"]})
    
    # Verify current password
    if not verify_password(password_data.currentPassword, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {
            "hashed_password": hash_password(password_data.newPassword),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"success": True, "message": "Password changed successfully"}
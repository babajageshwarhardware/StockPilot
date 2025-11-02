from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from motor.motor_asyncio import AsyncIOMotorClient
from middleware.auth import get_current_user
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import os

router = APIRouter(prefix="/customers", tags=["Customers"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new customer"""
    # Check if phone already exists
    existing = await db.customers.find_one({"phone": customer_data.phone})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this phone number already exists"
        )
    
    # Create customer document
    customer_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    customer_doc = customer_data.model_dump()
    customer_doc["id"] = customer_id
    customer_doc["createdAt"] = now.isoformat()
    customer_doc["updatedAt"] = now.isoformat()
    
    await db.customers.insert_one(customer_doc)
    
    customer_doc.pop("_id")
    return customer_doc

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None
):
    """Get all customers with search"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    skip = (page - 1) * limit
    
    customers = await db.customers.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single customer by ID"""
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a customer"""
    # Check if customer exists
    existing = await db.customers.find_one({"id": customer_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Prepare update data
    update_data = customer_data.model_dump(exclude_unset=True)
    update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    
    await db.customers.update_one({"id": customer_id}, {"$set": update_data})
    
    updated_customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    return updated_customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a customer"""
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return {"success": True, "message": "Customer deleted successfully"}
from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from motor.motor_asyncio import AsyncIOMotorClient
from middleware.auth import get_current_user
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import os

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new supplier"""
    # Check if phone already exists
    existing = await db.suppliers.find_one({"phone": supplier_data.phone})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier with this phone number already exists"
        )
    
    # Create supplier document
    supplier_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    supplier_doc = supplier_data.model_dump()
    supplier_doc["id"] = supplier_id
    supplier_doc["createdAt"] = now.isoformat()
    supplier_doc["updatedAt"] = now.isoformat()
    
    await db.suppliers.insert_one(supplier_doc)
    
    supplier_doc.pop("_id")
    return supplier_doc

@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None
):
    """Get all suppliers with search"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    skip = (page - 1) * limit
    
    suppliers = await db.suppliers.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return suppliers

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single supplier by ID"""
    supplier = await db.suppliers.find_one({"id": supplier_id}, {"_id": 0})
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return supplier

@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a supplier"""
    # Check if supplier exists
    existing = await db.suppliers.find_one({"id": supplier_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Prepare update data
    update_data = supplier_data.model_dump(exclude_unset=True)
    update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    
    await db.suppliers.update_one({"id": supplier_id}, {"$set": update_data})
    
    updated_supplier = await db.suppliers.find_one({"id": supplier_id}, {"_id": 0})
    return updated_supplier

@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a supplier"""
    result = await db.suppliers.delete_one({"id": supplier_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return {"success": True, "message": "Supplier deleted successfully"}
from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.product import ProductCreate, ProductUpdate, ProductResponse
from motor.motor_asyncio import AsyncIOMotorClient
from middleware.auth import get_current_user
from datetime import datetime, timezone
from typing import List, Optional
import uuid
import os

router = APIRouter(prefix="/products", tags=["Products"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new product"""
    # Check if SKU already exists
    existing = await db.products.find_one({"sku": product_data.sku.upper()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )
    
    # Create product document
    product_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    product_doc = product_data.model_dump()
    product_doc["id"] = product_id
    product_doc["sku"] = product_data.sku.upper()
    product_doc["createdBy"] = current_user["id"]
    product_doc["createdAt"] = now.isoformat()
    product_doc["updatedAt"] = now.isoformat()
    
    # Calculate profit margin
    if product_data.pricing.purchasePrice > 0:
        profit_margin = ((product_data.pricing.sellingPrice - product_data.pricing.purchasePrice) / product_data.pricing.purchasePrice) * 100
        product_doc["profitMargin"] = round(profit_margin, 2)
    else:
        product_doc["profitMargin"] = 0
    
    await db.products.insert_one(product_doc)
    
    product_doc.pop("_id")
    return product_doc

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    lowStock: bool = False
):
    """Get all products with filters"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"sku": {"$regex": search, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    if brand:
        query["brand"] = brand
    
    if lowStock:
        query["$expr"] = {"$lte": ["$stock.quantity", "$stock.reorderPoint"]}
    
    skip = (page - 1) * limit
    
    products = await db.products.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return products

@router.get("/categories")
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Get all unique categories"""
    categories = await db.products.distinct("category")
    return {"categories": categories}

@router.get("/brands")
async def get_brands(current_user: dict = Depends(get_current_user)):
    """Get all unique brands"""
    brands = await db.products.distinct("brand")
    return {"brands": brands}

@router.get("/low-stock")
async def get_low_stock_products(current_user: dict = Depends(get_current_user)):
    """Get products below reorder point"""
    products = await db.products.find(
        {"$expr": {"$lte": ["$stock.quantity", "$stock.reorderPoint"]}},
        {"_id": 0}
    ).to_list(100)
    return {"lowStockItems": products, "count": len(products)}

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single product by ID"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a product"""
    # Check if product exists
    existing = await db.products.find_one({"id": product_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Prepare update data
    update_data = product_data.model_dump(exclude_unset=True)
    update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    
    # Recalculate profit margin if pricing updated
    if "pricing" in update_data:
        pricing = {**existing.get("pricing", {}), **update_data["pricing"]}
        if pricing.get("purchasePrice", 0) > 0:
            profit_margin = ((pricing["sellingPrice"] - pricing["purchasePrice"]) / pricing["purchasePrice"]) * 100
            update_data["profitMargin"] = round(profit_margin, 2)
    
    await db.products.update_one({"id": product_id}, {"$set": update_data})
    
    updated_product = await db.products.find_one({"id": product_id}, {"_id": 0})
    return updated_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a product"""
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return {"success": True, "message": "Product deleted successfully"}
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response
from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from bson import ObjectId

from models.sale import (
    SaleCreate, SaleUpdate, SaleResponse, SaleReturn, SaleStats,
    PaymentStatus
)
from models.transaction import TransactionCreate, TransactionType, TransactionStatus
from routes.auth import get_current_user
from utils.invoice_generator import generate_invoice_pdf

router = APIRouter(prefix="/sales", tags=["sales"])

# Get MongoDB client
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def generate_invoice_number():
    """Generate unique invoice number"""
    today = datetime.now().strftime("%Y%m%d")
    # Find the last invoice of the day
    last_sale = await db.sales.find_one(
        {"invoiceNumber": {"$regex": f"^INV-{today}"}},
        sort=[("invoiceNumber", -1)]
    )
    
    if last_sale:
        last_num = int(last_sale["invoiceNumber"].split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"INV-{today}-{new_num:04d}"

async def update_product_stock(product_id: str, quantity: float, operation: str = "subtract"):
    """Update product stock quantity"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    current_qty = product.get("stock", {}).get("quantity", 0)
    
    if operation == "subtract":
        new_qty = current_qty - quantity
        if new_qty < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product['name']}. Available: {current_qty}"
            )
    else:  # add
        new_qty = current_qty + quantity
    
    await db.products.update_one(
        {"id": product_id},
        {"$set": {"stock.quantity": new_qty, "updatedAt": datetime.now()}}
    )

@router.post("", response_model=SaleResponse, status_code=201)
async def create_sale(sale: SaleCreate, current_user: dict = Depends(get_current_user)):
    """Create a new sale and update inventory"""
    
    # Generate invoice number
    invoice_number = await generate_invoice_number()
    
    # Create sale document
    sale_id = str(uuid.uuid4())
    sale_data = sale.model_dump()
    sale_data.update({
        "id": sale_id,
        "invoiceNumber": invoice_number,
        "saleDate": datetime.now(),
        "createdBy": current_user["id"],
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })
    
    # Update stock for each item
    try:
        for item in sale.items:
            await update_product_stock(item.productId, item.quantity, "subtract")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock update failed: {str(e)}")
    
    # Insert sale
    await db.sales.insert_one(sale_data)
    
    # Create transaction record
    transaction_data = TransactionCreate(
        referenceId=sale_id,
        referenceType=TransactionType.SALE,
        amount=sale.total,
        paymentMode=sale.paymentMode.value,
        description=f"Sale invoice {invoice_number}",
        status=TransactionStatus.SUCCESS if sale.paymentStatus == PaymentStatus.PAID else TransactionStatus.PENDING
    )
    
    transaction_id = str(uuid.uuid4())
    transaction_doc = transaction_data.model_dump()
    transaction_doc.update({
        "id": transaction_id,
        "transactionDate": datetime.now(),
        "createdBy": current_user["id"],
        "createdAt": datetime.now()
    })
    await db.transactions.insert_one(transaction_doc)
    
    return SaleResponse(**sale_data)

@router.get("", response_model=List[SaleResponse])
async def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payment_status: Optional[str] = None,
    customer_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get list of sales with filters"""
    
    query = {}
    
    # Date filter
    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            date_query["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        if date_query:
            query["saleDate"] = date_query
    
    # Payment status filter
    if payment_status:
        query["paymentStatus"] = payment_status
    
    # Customer filter
    if customer_id:
        query["customerId"] = customer_id
    
    sales = await db.sales.find(query).sort("saleDate", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [SaleResponse(**sale) for sale in sales]

@router.get("/stats", response_model=SaleStats)
async def get_sales_stats(current_user: dict = Depends(get_current_user)):
    """Get sales statistics"""
    
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # Aggregate sales data
    pipeline = [
        {
            "$facet": {
                "totalSales": [
                    {"$group": {"_id": None, "total": {"$sum": "$total"}, "count": {"$sum": 1}}}
                ],
                "todaySales": [
                    {"$match": {"saleDate": {"$gte": today_start}}},
                    {"$group": {"_id": None, "total": {"$sum": "$total"}}}
                ],
                "weekSales": [
                    {"$match": {"saleDate": {"$gte": week_start}}},
                    {"$group": {"_id": None, "total": {"$sum": "$total"}}}
                ],
                "monthSales": [
                    {"$match": {"saleDate": {"$gte": month_start}}},
                    {"$group": {"_id": None, "total": {"$sum": "$total"}}}
                ],
                "topProducts": [
                    {"$unwind": "$items"},
                    {"$group": {
                        "_id": "$items.productId",
                        "productName": {"$first": "$items.productName"},
                        "totalQuantity": {"$sum": "$items.quantity"},
                        "totalRevenue": {"$sum": "$items.lineTotal"}
                    }},
                    {"$sort": {"totalRevenue": -1}},
                    {"$limit": 5}
                ]
            }
        }
    ]
    
    result = await db.sales.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return SaleStats(
            totalSales=0,
            totalTransactions=0,
            averageOrderValue=0,
            todaySales=0,
            weekSales=0,
            monthSales=0,
            topProducts=[],
            recentSales=[]
        )
    
    data = result[0]
    total_sales = data["totalSales"][0] if data["totalSales"] else {"total": 0, "count": 0}
    today_sales = data["todaySales"][0] if data["todaySales"] else {"total": 0}
    week_sales = data["weekSales"][0] if data["weekSales"] else {"total": 0}
    month_sales = data["monthSales"][0] if data["monthSales"] else {"total": 0}
    
    # Get recent sales
    recent_sales = await db.sales.find().sort("saleDate", -1).limit(5).to_list(length=5)
    
    # Format top products
    top_products = [
        {
            "productId": item["_id"],
            "productName": item["productName"],
            "totalQuantity": item["totalQuantity"],
            "totalRevenue": item["totalRevenue"]
        }
        for item in data["topProducts"]
    ]
    
    return SaleStats(
        totalSales=total_sales["total"],
        totalTransactions=total_sales["count"],
        averageOrderValue=total_sales["total"] / total_sales["count"] if total_sales["count"] > 0 else 0,
        todaySales=today_sales["total"],
        weekSales=week_sales["total"],
        monthSales=month_sales["total"],
        topProducts=top_products,
        recentSales=[SaleResponse(**sale) for sale in recent_sales]
    )

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(sale_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single sale by ID"""
    
    sale = await db.sales.find_one({"id": sale_id})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    return SaleResponse(**sale)

@router.get("/{sale_id}/invoice")
async def get_invoice_pdf(sale_id: str, current_user: dict = Depends(get_current_user)):
    """Generate and download invoice PDF"""
    
    sale = await db.sales.find_one({"id": sale_id})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Generate PDF
    pdf_bytes = generate_invoice_pdf(sale)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{sale['invoiceNumber']}.pdf"
        }
    )

@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: str,
    sale_update: SaleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update sale details (limited fields)"""
    
    sale = await db.sales.find_one({"id": sale_id})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    update_data = sale_update.model_dump(exclude_unset=True)
    update_data["updatedAt"] = datetime.now()
    
    await db.sales.update_one(
        {"id": sale_id},
        {"$set": update_data}
    )
    
    updated_sale = await db.sales.find_one({"id": sale_id})
    return SaleResponse(**updated_sale)

@router.post("/{sale_id}/return")
async def process_return(
    sale_id: str,
    return_data: SaleReturn,
    current_user: dict = Depends(get_current_user)
):
    """Process sale return and refund"""
    
    sale = await db.sales.find_one({"id": sale_id})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Validate return items exist in original sale
    sale_items = {item["productId"]: item for item in sale["items"]}
    
    for return_item in return_data.items:
        if return_item.productId not in sale_items:
            raise HTTPException(
                status_code=400,
                detail=f"Product {return_item.productId} not found in original sale"
            )
        
        original_qty = sale_items[return_item.productId]["quantity"]
        if return_item.quantity > original_qty:
            raise HTTPException(
                status_code=400,
                detail=f"Return quantity exceeds original quantity for product {return_item.productId}"
            )
    
    # Update stock (add back returned items)
    for return_item in return_data.items:
        await update_product_stock(return_item.productId, return_item.quantity, "add")
    
    # Update sale status
    await db.sales.update_one(
        {"id": sale_id},
        {
            "$set": {
                "paymentStatus": PaymentStatus.REFUNDED.value,
                "updatedAt": datetime.now()
            }
        }
    )
    
    # Create refund transaction
    transaction_id = str(uuid.uuid4())
    transaction_doc = {
        "id": transaction_id,
        "referenceId": sale_id,
        "referenceType": TransactionType.REFUND.value,
        "amount": return_data.refundAmount,
        "paymentMode": return_data.refundMode.value,
        "description": return_data.reason or f"Refund for invoice {sale['invoiceNumber']}",
        "status": TransactionStatus.SUCCESS.value,
        "transactionDate": datetime.now(),
        "createdBy": current_user["id"],
        "createdAt": datetime.now()
    }
    await db.transactions.insert_one(transaction_doc)
    
    return {
        "message": "Return processed successfully",
        "refundAmount": return_data.refundAmount,
        "transactionId": transaction_id
    }

@router.delete("/{sale_id}")
async def delete_sale(sale_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a sale (soft delete - mark as cancelled)"""
    
    sale = await db.sales.find_one({"id": sale_id})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Restore stock
    for item in sale["items"]:
        await update_product_stock(item["productId"], item["quantity"], "add")
    
    # Mark as cancelled instead of deleting
    await db.sales.update_one(
        {"id": sale_id},
        {
            "$set": {
                "paymentStatus": "cancelled",
                "updatedAt": datetime.now()
            }
        }
    )
    
    return {"message": "Sale cancelled successfully"}

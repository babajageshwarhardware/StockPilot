"""Seed script to create default admin user and sample data"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from utils.security import hash_password
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def seed_database():
    """Seed database with default admin and sample data"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🌱 Starting database seeding...")
    
    # Create default admin user
    admin_email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@stockpilot.com')
    existing_admin = await db.users.find_one({"email": admin_email})
    
    if not existing_admin:
        admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'Admin@123456')
        admin_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        admin_user = {
            "id": admin_id,
            "name": "Admin User",
            "email": admin_email,
            "hashed_password": hash_password(admin_password),
            "role": "admin",
            "phone": "9999999999",
            "permissions": [
                "view_sales", "create_sales", "edit_sales", "delete_sales",
                "view_products", "create_products", "edit_products", "delete_products",
                "view_purchases", "create_purchases", "edit_purchases", "delete_purchases",
                "view_analytics", "view_reports", "manage_users"
            ],
            "isActive": True,
            "lastLogin": None,
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat()
        }
        
        await db.users.insert_one(admin_user)
        print(f"✅ Admin user created:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
    else:
        print("ℹ️  Admin user already exists")
    
    # Create sample categories and products
    sample_products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Laptop",
            "sku": "ELEC-LAP-001",
            "description": "High-performance laptop for business",
            "category": "Electronics",
            "brand": "TechBrand",
            "unit": "piece",
            "pricing": {
                "purchasePrice": 40000,
                "sellingPrice": 50000,
                "mrp": 55000,
                "discount": 0,
                "taxRate": 18
            },
            "stock": {
                "quantity": 25,
                "reorderPoint": 5,
                "warehouse": "Main"
            },
            "profitMargin": 25.0,
            "isActive": True,
            "createdBy": existing_admin["id"] if existing_admin else admin_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wireless Mouse",
            "sku": "ELEC-MSE-001",
            "description": "Ergonomic wireless mouse",
            "category": "Electronics",
            "brand": "TechBrand",
            "unit": "piece",
            "pricing": {
                "purchasePrice": 300,
                "sellingPrice": 450,
                "mrp": 500,
                "discount": 0,
                "taxRate": 18
            },
            "stock": {
                "quantity": 100,
                "reorderPoint": 20,
                "warehouse": "Main"
            },
            "profitMargin": 50.0,
            "isActive": True,
            "createdBy": existing_admin["id"] if existing_admin else admin_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Office Chair",
            "sku": "FURN-CHR-001",
            "description": "Comfortable ergonomic office chair",
            "category": "Furniture",
            "brand": "ComfortSeating",
            "unit": "piece",
            "pricing": {
                "purchasePrice": 3000,
                "sellingPrice": 4500,
                "mrp": 5000,
                "discount": 10,
                "taxRate": 18
            },
            "stock": {
                "quantity": 15,
                "reorderPoint": 5,
                "warehouse": "Main"
            },
            "profitMargin": 50.0,
            "isActive": True,
            "createdBy": existing_admin["id"] if existing_admin else admin_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    existing_products = await db.products.count_documents({})
    if existing_products == 0:
        await db.products.insert_many(sample_products)
        print(f"✅ Created {len(sample_products)} sample products")
    else:
        print(f"ℹ️  Products already exist ({existing_products} products)")
    
    # Create sample customers
    sample_customers = [
        {
            "id": str(uuid.uuid4()),
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "9876543210",
            "gstNumber": "27AABCU9603R1ZM",
            "address": {
                "street": "123 Main Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "country": "India"
            },
            "loyaltyPoints": 150,
            "creditLimit": 50000,
            "outstandingBalance": 0,
            "isActive": True,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "9876543211",
            "address": {
                "street": "456 Park Avenue",
                "city": "Delhi",
                "state": "Delhi",
                "pincode": "110001",
                "country": "India"
            },
            "loyaltyPoints": 200,
            "creditLimit": 75000,
            "outstandingBalance": 0,
            "isActive": True,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    existing_customers = await db.customers.count_documents({})
    if existing_customers == 0:
        await db.customers.insert_many(sample_customers)
        print(f"✅ Created {len(sample_customers)} sample customers")
    else:
        print(f"ℹ️  Customers already exist ({existing_customers} customers)")
    
    # Create sample suppliers
    sample_suppliers = [
        {
            "id": str(uuid.uuid4()),
            "name": "TechSupplies Inc",
            "email": "contact@techsupplies.com",
            "phone": "9876543220",
            "gstNumber": "27AABCT1234R1ZM",
            "address": {
                "street": "789 Industrial Area",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560001",
                "country": "India"
            },
            "paymentTerms": "net30",
            "outstandingBalance": 0,
            "rating": 4.5,
            "isActive": True,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    existing_suppliers = await db.suppliers.count_documents({})
    if existing_suppliers == 0:
        await db.suppliers.insert_many(sample_suppliers)
        print(f"✅ Created {len(sample_suppliers)} sample suppliers")
    else:
        print(f"ℹ️  Suppliers already exist ({existing_suppliers} suppliers)")
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.products.create_index("sku", unique=True)
    await db.products.create_index([("name", "text"), ("description", "text")])
    await db.customers.create_index("phone")
    await db.suppliers.create_index("phone")
    print("✅ Database indexes created")
    
    client.close()
    print("\n🎉 Database seeding completed successfully!")
    print("\n📝 Login credentials:")
    print(f"   Email: {admin_email}")
    print(f"   Password: {os.environ.get('DEFAULT_ADMIN_PASSWORD', 'Admin@123456')}")

if __name__ == "__main__":
    asyncio.run(seed_database())
"""
Quick database initialization script for local demo
Creates tables and adds sample data
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.discount import Discount
from sqlalchemy import inspect

def init_database():
    """Initialize database with tables and sample data"""
    
    print("🗄️  Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    # Check what tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📊 Created tables: {', '.join(tables)}")
    
    # Add sample data
    db = SessionLocal()
    try:
        # Check if we already have data
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"⚠️  Database already has {existing_products} products. Skipping sample data.")
            return
        
        print("\n📦 Adding sample products...")
        
        # Add sample products
        products = [
            Product(
                name="Premium Laptop",
                description="High-performance laptop with 16GB RAM and 512GB SSD",
                price=999.99,
                stock_quantity=10,
                is_active=True
            ),
            Product(
                name="Wireless Mouse",
                description="Ergonomic wireless mouse with precision tracking",
                price=29.99,
                stock_quantity=50,
                is_active=True
            ),
            Product(
                name="Mechanical Keyboard",
                description="RGB mechanical keyboard with Cherry MX switches",
                price=79.99,
                stock_quantity=25,
                is_active=True
            ),
            Product(
                name="4K Monitor",
                description="27-inch 4K UHD monitor with HDR support",
                price=399.99,
                stock_quantity=15,
                is_active=True
            ),
            Product(
                name="USB-C Hub",
                description="7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader",
                price=49.99,
                stock_quantity=30,
                is_active=True
            ),
        ]
        
        for product in products:
            db.add(product)
        
        db.commit()
        print(f"✅ Added {len(products)} sample products!")
        
        # Add sample discounts
        print("\n💰 Adding sample discounts...")
        
        # Get first product for discount
        laptop = db.query(Product).filter(Product.name == "Premium Laptop").first()
        mouse = db.query(Product).filter(Product.name == "Wireless Mouse").first()
        
        discounts = []
        
        if laptop:
            discounts.append(Discount(
                product_id=laptop.id,
                discount_type="percentage",
                discount_value=10.0,
                min_quantity=2,
                is_active=True
            ))
        
        if mouse:
            discounts.append(Discount(
                product_id=mouse.id,
                discount_type="buy_x_get_y",
                discount_value=1.0,  # Buy 2 get 1 free
                min_quantity=2,
                is_active=True
            ))
        
        for discount in discounts:
            db.add(discount)
        
        db.commit()
        print(f"✅ Added {len(discounts)} sample discounts!")
        
        print("\n" + "="*50)
        print("🎉 Database initialized successfully!")
        print("="*50)
        print("\n📋 Summary:")
        print(f"   • {len(products)} products")
        print(f"   • {len(discounts)} discounts")
        print(f"   • Ready for demo!")
        print("\n🚀 Start the backend server:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

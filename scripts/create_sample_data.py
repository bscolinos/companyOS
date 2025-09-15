#!/usr/bin/env python3

"""
Sample data creation script for AI-Powered Ecommerce Platform
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_db_connection
from backend.database.models import User, Category, Product
from backend.database.operations import UserOperations, ProductOperations
from passlib.context import CryptContext
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_sample_data():
    """Create sample data for the platform"""
    conn = get_db_connection()
    
    try:
        print("Creating sample data...")
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        admin_id = UserOperations.create_user(conn, admin_user)
        
        # Create regular user
        regular_user = User(
            email="user@example.com",
            username="user",
            hashed_password=pwd_context.hash("user123"),
            first_name="John",
            last_name="Doe"
        )
        user_id = UserOperations.create_user(conn, regular_user)
        
        # Create categories
        categories = [
            {"name": "Electronics", "description": "Electronic devices and gadgets"},
            {"name": "Clothing", "description": "Fashion and apparel"},
            {"name": "Home & Garden", "description": "Home improvement and garden supplies"},
            {"name": "Books", "description": "Books and educational materials"},
            {"name": "Sports", "description": "Sports and outdoor equipment"}
        ]
        
        category_ids = []
        cursor = conn.cursor()
        for cat_data in categories:
            cursor.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", 
                          (cat_data["name"], cat_data["description"]))
            category_ids.append(cursor.lastrowid)
        conn.commit()
        
        # Create sample products
        products = [
            {
                "name": "Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "sku": "WBH-001",
                "category_id": category_ids[0],
                "base_price": 199.99,
                "current_price": 179.99,
                "cost_price": 120.00,
                "stock_quantity": 50,
                "min_stock_level": 10,
                "max_stock_level": 200,
                "weight": 0.3,
                "dimensions": {"length": 20, "width": 15, "height": 8},
                "images": ["https://example.com/headphones1.jpg"],
                "tags": ["bluetooth", "wireless", "audio", "electronics"],
                "is_featured": True,
                "demand_score": 0.8
            },
            {
                "name": "Smart Fitness Watch",
                "description": "Advanced fitness tracking with heart rate monitor",
                "sku": "SFW-002",
                "category_id": category_ids[0],
                "base_price": 299.99,
                "current_price": 279.99,
                "cost_price": 180.00,
                "stock_quantity": 30,
                "min_stock_level": 5,
                "max_stock_level": 100,
                "weight": 0.1,
                "dimensions": {"length": 5, "width": 4, "height": 1},
                "images": ["https://example.com/watch1.jpg"],
                "tags": ["fitness", "smart", "health", "wearable"],
                "is_featured": True,
                "demand_score": 0.9
            },
            {
                "name": "Organic Cotton T-Shirt",
                "description": "Comfortable organic cotton t-shirt in various colors",
                "sku": "OCT-003",
                "category_id": category_ids[1],
                "base_price": 29.99,
                "current_price": 24.99,
                "cost_price": 15.00,
                "stock_quantity": 100,
                "min_stock_level": 20,
                "max_stock_level": 500,
                "weight": 0.2,
                "dimensions": {"length": 30, "width": 25, "height": 2},
                "images": ["https://example.com/tshirt1.jpg"],
                "tags": ["clothing", "organic", "cotton", "casual"],
                "is_featured": False,
                "demand_score": 0.6
            },
            {
                "name": "Smart Home Security Camera",
                "description": "WiFi-enabled security camera with night vision",
                "sku": "SHSC-004",
                "category_id": category_ids[2],
                "base_price": 149.99,
                "current_price": 129.99,
                "cost_price": 80.00,
                "stock_quantity": 25,
                "min_stock_level": 5,
                "max_stock_level": 100,
                "weight": 0.5,
                "dimensions": {"length": 12, "width": 8, "height": 8},
                "images": ["https://example.com/camera1.jpg"],
                "tags": ["security", "smart", "camera", "home"],
                "is_featured": True,
                "demand_score": 0.7
            },
            {
                "name": "Programming Fundamentals Book",
                "description": "Complete guide to programming fundamentals",
                "sku": "PFB-005",
                "category_id": category_ids[3],
                "base_price": 49.99,
                "current_price": 39.99,
                "cost_price": 25.00,
                "stock_quantity": 75,
                "min_stock_level": 15,
                "max_stock_level": 200,
                "weight": 0.8,
                "dimensions": {"length": 24, "width": 18, "height": 3},
                "images": ["https://example.com/book1.jpg"],
                "tags": ["book", "programming", "education", "technology"],
                "is_featured": False,
                "demand_score": 0.5
            },
            {
                "name": "Professional Basketball",
                "description": "Official size basketball for professional play",
                "sku": "PB-006",
                "category_id": category_ids[4],
                "base_price": 79.99,
                "current_price": 69.99,
                "cost_price": 40.00,
                "stock_quantity": 40,
                "min_stock_level": 10,
                "max_stock_level": 150,
                "weight": 0.6,
                "dimensions": {"length": 25, "width": 25, "height": 25},
                "images": ["https://example.com/basketball1.jpg"],
                "tags": ["sports", "basketball", "outdoor", "equipment"],
                "is_featured": False,
                "demand_score": 0.4
            }
        ]
        
        for product_data in products:
            product = Product(**product_data)
            ProductOperations.create_product(conn, product)
        
        print("✅ Sample data created successfully!")
        print(f"   - Created {len(categories)} categories")
        print(f"   - Created {len(products)} products")
        print("   - Created admin user (admin@example.com / admin123)")
        print("   - Created regular user (user@example.com / user123)")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_sample_data()

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import math
from datetime import datetime, timedelta
from database.models import User
from api.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Application-layer product store
class ProductStore:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes
        self.products = self._create_products()  # Always use fresh original products
        logger.info(f"ProductStore initialized with {len(self.products)} products at original prices")
    
    def _create_products(self):
        """Create application-layer cached products"""
        return [
            {
                "id": 1,
                "name": "Premium Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
                "sku": "WH-001",
                "category_id": 1,
                "category_name": "Electronics",
                "base_price": 199.99,
                "current_price": 179.99,
                "stock_quantity": 25,
                "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400", "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400"],
                "tags": ["electronics", "audio", "wireless"],
                "is_active": True,
                "is_featured": True,
                "demand_score": 0.85,
                "price_elasticity": -1.2
            },
            {
                "id": 2,
                "name": "Smart Home Hub",
                "description": "Control all your smart devices from one central hub with voice commands and mobile app.",
                "sku": "SH-002",
                "category_id": 1,
                "category_name": "Electronics",
                "base_price": 149.99,
                "current_price": 139.99,
                "stock_quantity": 18,
                "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "https://images.unsplash.com/photo-1518444065439-e933c06ce9cd?w=400"],
                "tags": ["smart home", "electronics", "automation"],
                "is_active": True,
                "is_featured": True,
                "demand_score": 0.78,
                "price_elasticity": -1.5
            },
            {
                "id": 3,
                "name": "Organic Coffee Blend",
                "description": "Premium organic coffee beans sourced from sustainable farms. Rich flavor with notes of chocolate and caramel.",
                "sku": "CF-003",
                "category_id": 2,
                "category_name": "Food & Beverages",
                "base_price": 24.99,
                "current_price": 22.99,
                "stock_quantity": 45,
                "images": ["https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400", "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400"],
                "tags": ["coffee", "organic", "premium"],
                "is_active": True,
                "is_featured": True,
                "demand_score": 0.91,
                "price_elasticity": -1.8
            },
            {
                "id": 4,
                "name": "Ergonomic Office Chair",
                "description": "Professional ergonomic chair with lumbar support, adjustable height, and breathable mesh fabric for all-day comfort.",
                "sku": "OC-004",
                "category_id": 3,
                "category_name": "Furniture",
                "base_price": 299.99,
                "current_price": 279.99,
                "stock_quantity": 12,
                "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400", "https://images.unsplash.com/photo-1541558869434-2840d308329a?w=400", "https://images.unsplash.com/photo-1549497538-303791108f95?w=400"],
                "tags": ["furniture", "office", "ergonomic", "comfort"],
                "is_active": True,
                "is_featured": False,
                "demand_score": 0.72,
                "price_elasticity": -0.8
            },
            {
                "id": 5,
                "name": "Fitness Tracking Watch",
                "description": "Advanced fitness tracker with heart rate monitoring, GPS tracking, sleep analysis, and 7-day battery life.",
                "sku": "FT-005",
                "category_id": 1,
                "category_name": "Electronics",
                "base_price": 249.99,
                "current_price": 229.99,
                "stock_quantity": 33,
                "images": ["https://images.unsplash.com/photo-1544117519-31a4b719223d?w=400", "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=400", "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400"],
                "tags": ["fitness", "electronics", "wearable", "health"],
                "is_active": True,
                "is_featured": True,
                "demand_score": 0.88,
                "price_elasticity": -1.1
            }
        ]
    
    def reset_prices(self):
        """Public method to reset prices during demo"""
        self.products = self._create_products()  # Always recreate with original values
        self.invalidate_all()  # Clear cache to reflect reset
        logger.info("Product prices manually reset to original values")
    
    def get(self, key: str):
        """Get cached data if still valid"""
        if key in self.cache and key in self.cache_time:
            if datetime.now() - self.cache_time[key] < timedelta(seconds=self.cache_duration):
                return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cached data with timestamp"""
        self.cache[key] = value
        self.cache_time[key] = datetime.now()
    
    def get_products(self, page: int = 1, per_page: int = 12, category_id: Optional[int] = None, 
                    search: Optional[str] = None, is_featured: Optional[bool] = None,
                    min_price: Optional[float] = None, max_price: Optional[float] = None,
                    in_stock_only: bool = True):
        """Return filtered and paginated products from application cache"""
        # Apply filters
        filtered_products = []
        seen_skus = set()  # Deduplication by SKU
        
        for product in self.products:
            # Skip duplicates
            if product["sku"] in seen_skus:
                continue
            seen_skus.add(product["sku"])
            
            # Apply filters
            if category_id is not None and product["category_id"] != category_id:
                continue
            if is_featured is not None and product["is_featured"] != is_featured:
                continue
            if min_price is not None and product["current_price"] < min_price:
                continue
            if max_price is not None and product["current_price"] > max_price:
                continue
            if in_stock_only and product["stock_quantity"] <= 0:
                continue
            if search and search.lower() not in product["name"].lower() and search.lower() not in product["description"].lower():
                continue
                
            filtered_products.append(product)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return {
            "items": filtered_products[start_idx:end_idx],
            "total": len(filtered_products),
            "page": page,
            "per_page": per_page,
            "pages": math.ceil(len(filtered_products) / per_page) if per_page > 0 else 1
        }
    
    def invalidate_all(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_time.clear()
        logger.info("All product cache cleared")
    
    def invalidate_pattern(self, pattern: str):
        """Clear cached data matching a pattern"""
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.cache[key]
            del self.cache_time[key]
        logger.info(f"Cleared {len(keys_to_remove)} cache entries matching pattern: {pattern}")

# Global product store instance
product_cache = ProductStore()

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    sku: str
    category_id: Optional[int]
    category_name: Optional[str]
    base_price: float
    current_price: float
    stock_quantity: int
    images: Optional[List[str]]
    tags: Optional[List[str]]
    is_active: bool
    is_featured: bool
    demand_score: float
    price_elasticity: float

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    category_id: Optional[int] = None
    base_price: float
    current_price: float
    cost_price: Optional[float] = None
    stock_quantity: int = 0
    min_stock_level: int = 10
    max_stock_level: int = 1000
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_featured: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    current_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool

class PaginatedProductResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    per_page: int
    pages: int

@router.get("/", response_model=PaginatedProductResponse)
async def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    skip: Optional[int] = Query(None, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    is_featured: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = True,
):
    """Get products with filtering and pagination from application cache"""
    
    # Handle both pagination styles (page/per_page or skip/limit)
    if skip is not None and limit is not None:
        # Legacy skip/limit style
        actual_page = (skip // limit) + 1 if limit > 0 else 1
        actual_per_page = limit
    else:
        # Modern page/per_page style
        actual_page = page
        actual_per_page = per_page
    
    # Create cache key for this request
    cache_key = f"products_{actual_page}_{actual_per_page}_{category_id}_{search}_{is_featured}_{min_price}_{max_price}_{in_stock_only}"
    
    # Try to get from cache first
    cached_result = product_cache.get(cache_key)
    if cached_result:
        logger.info(f"Returning cached products for key: {cache_key}")
        return PaginatedProductResponse(**cached_result)
    
    # Get products from application cache
    products_data = product_cache.get_products(
        page=actual_page,
        per_page=actual_per_page,
        category_id=category_id,
        search=search,
        is_featured=is_featured,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only
    )
    
    # Convert to response format
    result = []
    for product_data in products_data["items"]:
        result.append(ProductResponse(
            id=product_data["id"],
            name=product_data["name"],
            description=product_data["description"],
            sku=product_data["sku"],
            category_id=product_data["category_id"],
            category_name=product_data["category_name"],
            base_price=product_data["base_price"],
            current_price=product_data["current_price"],
            stock_quantity=product_data["stock_quantity"],
            images=product_data["images"],
            tags=product_data["tags"],
            is_active=product_data["is_active"],
            is_featured=product_data["is_featured"],
            demand_score=product_data["demand_score"],
            price_elasticity=product_data["price_elasticity"]
        ))
    
    response_data = {
        "items": [item.dict() for item in result],
        "total": products_data["total"],
        "page": products_data["page"],
        "per_page": products_data["per_page"],
        "pages": products_data["pages"]
    }
    
    # Cache the result
    product_cache.set(cache_key, response_data)
    logger.info(f"Cached products for key: {cache_key}")
    
    return PaginatedProductResponse(**response_data)

@router.get("/featured")
async def get_featured_products():
    """Get featured products from application cache"""
    cache_key = "featured_products"
    
    # Try cache first
    cached_result = product_cache.get(cache_key)
    if cached_result:
        logger.info("Returning cached featured products")
        return cached_result
    
    # Get featured products from application cache
    products_data = product_cache.get_products(page=1, per_page=10, is_featured=True)
    
    result = []
    for product_data in products_data["items"]:
        result.append({
            "id": product_data["id"],
            "name": product_data["name"],
            "description": product_data["description"],
            "price": product_data["current_price"],
            "stock_quantity": product_data["stock_quantity"],
            "images": product_data["images"],
            "is_featured": product_data["is_featured"]
        })
    
    # Cache the result
    product_cache.set(cache_key, result)
    logger.info("Cached featured products")
    return result

@router.get("/health")
async def products_health_check():
    """Quick health check for products API"""
    try:
        # Test cache functionality
        test_data = product_cache.get_products(1, 1)
        return {
            "status": "healthy",
            "cache_working": True,
            "products_available": len(test_data["items"]) > 0,
            "product_count": len(product_cache.products)
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "cache_working": False
        }

@router.post("/cache/clear")
async def clear_product_cache():
    """Clear all product cache - useful for testing or after bulk updates"""
    try:
        product_cache.invalidate_all()
        return {"message": "Product cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-prices")
async def reset_product_prices():
    """Reset all product prices to original values - useful for demo purposes"""
    try:
        product_cache.reset_prices()
        return {
            "message": "Product prices reset to original values successfully",
            "demo_reset": True,
            "products_reset": len(product_cache.products)
        }
    except Exception as e:
        logger.error(f"Error resetting prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug-prices")
async def debug_current_prices():
    """Debug endpoint to show current exact prices"""
    try:
        current_prices = []
        for product in product_cache.products:
            current_prices.append({
                "id": product["id"],
                "name": product["name"],
                "current_price": product["current_price"],
                "base_price": product["base_price"]
            })
        
        return {
            "debug": True,
            "timestamp": datetime.now().isoformat(),
            "prices": current_prices
        }
    except Exception as e:
        logger.error(f"Error getting debug prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get a specific product by ID from application cache"""
    # Find product in application cache
    for product_data in product_cache.products:
        if product_data["id"] == product_id and product_data["is_active"]:
            return ProductResponse(
                id=product_data["id"],
                name=product_data["name"],
                description=product_data["description"],
                sku=product_data["sku"],
                category_id=product_data["category_id"],
                category_name=product_data["category_name"],
                base_price=product_data["base_price"],
                current_price=product_data["current_price"],
                stock_quantity=product_data["stock_quantity"],
                images=product_data["images"],
                tags=product_data["tags"],
                is_active=product_data["is_active"],
                is_featured=product_data["is_featured"],
                demand_score=product_data["demand_score"],
                price_elasticity=product_data["price_elasticity"]
            )
    
    raise HTTPException(status_code=404, detail="Product not found")

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a new product (admin only) - Note: Products are now managed in application layer"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if SKU already exists
    for existing_product in product_cache.products:
        if existing_product["sku"] == product_data.sku:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    # Create new product ID (simple incrementing)
    new_id = max([p["id"] for p in product_cache.products]) + 1 if product_cache.products else 1
    
    # Create new product
    new_product = {
        "id": new_id,
        "name": product_data.name,
        "description": product_data.description,
        "sku": product_data.sku,
        "category_id": product_data.category_id,
        "category_name": "Custom",  # Default category name
        "base_price": product_data.base_price,
        "current_price": product_data.current_price,
        "stock_quantity": product_data.stock_quantity,
                "images": product_data.images or ["https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"],
        "tags": product_data.tags or [],
        "is_active": True,
        "is_featured": product_data.is_featured,
        "demand_score": 0.5,  # Default value
        "price_elasticity": -1.0  # Default value
    }
    
    # Add to cache
    product_cache.products.append(new_product)
    
    # Clear cache after creating product
    product_cache.invalidate_pattern("products_")
    
    return ProductResponse(**new_product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update a product (admin only) in application cache"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find and update product in cache
    for i, product in enumerate(product_cache.products):
        if product["id"] == product_id:
            # Update fields
            update_data = product_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field in product:
                    product[field] = value
            
            # Clear cache after updating product
            product_cache.invalidate_pattern("products_")
            
            return ProductResponse(**product)
    
    raise HTTPException(status_code=404, detail="Product not found")

@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories():
    """Get all product categories from application cache"""
    # Extract unique categories from products
    categories = {}
    for product in product_cache.products:
        if product["category_id"] not in categories:
            categories[product["category_id"]] = {
                "id": product["category_id"],
                "name": product["category_name"],
                "description": f"Category for {product['category_name']} products",
                "is_active": True
            }
    
    return [CategoryResponse(**cat) for cat in categories.values()]

@router.get("/{product_id}/recommendations")
async def get_product_recommendations(
    product_id: int,
    limit: int = Query(5, ge=1, le=20),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get recommendations for a specific product from application cache"""
    # Find the product
    target_product = None
    for product in product_cache.products:
        if product["id"] == product_id and product["is_active"]:
            target_product = product
            break
    
    if not target_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get similar products from same category
    recommendations = []
    for product in product_cache.products:
        if (product["category_id"] == target_product["category_id"] and 
            product["id"] != product_id and 
            product["is_active"] and 
            product["stock_quantity"] > 0):
            recommendations.append({
                "product_id": product["id"],
                "name": product["name"],
                "price": product["current_price"],
                "recommendation_score": product["demand_score"]
            })
    
    # Sort by demand score and limit
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    recommendations = recommendations[:limit]
    
    return {"recommendations": recommendations}

@router.get("/{product_id}/reviews")
async def get_product_reviews(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get reviews for a specific product - mock data since reviews are not in application cache"""
    # Verify product exists
    product_exists = any(p["id"] == product_id and p["is_active"] for p in product_cache.products)
    if not product_exists:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Return mock review data
    mock_reviews = [
        {
            "id": 1,
            "user_id": 1,
            "rating": 5,
            "title": "Excellent product!",
            "comment": "Really happy with this purchase. Great quality and fast delivery.",
            "is_verified_purchase": True,
            "helpful_votes": 12,
            "created_at": "2024-01-15T10:30:00"
        },
        {
            "id": 2,
            "user_id": 2,
            "rating": 4,
            "title": "Good value",
            "comment": "Works as expected. Good value for money.",
            "is_verified_purchase": True,
            "helpful_votes": 8,
            "created_at": "2024-01-10T14:20:00"
        }
    ]
    
    # Apply pagination
    paginated_reviews = mock_reviews[skip:skip + limit]
    
    return {
        "reviews": paginated_reviews,
        "statistics": {
            "total_reviews": len(mock_reviews),
            "average_rating": 4.5,
            "total_helpful_votes": 20
        }
    }

@router.get("/featured/")
async def get_featured_products_alt(
    limit: int = Query(10, ge=1, le=50)
):
    """Get featured products (alternative endpoint) from application cache"""
    # Get featured products from cache
    featured_products = [
        product for product in product_cache.products
        if product["is_featured"] and product["is_active"] and product["stock_quantity"] > 0
    ]
    
    # Sort by demand score and limit
    featured_products.sort(key=lambda x: x["demand_score"], reverse=True)
    featured_products = featured_products[:limit]
    
    return [
        {
            "id": product["id"],
            "name": product["name"],
            "current_price": product["current_price"],
            "images": product["images"],
            "demand_score": product["demand_score"]
        }
        for product in featured_products
    ]

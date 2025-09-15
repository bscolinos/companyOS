from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
import logging
from backend.database.connection import get_database
from backend.database.models import Product, Category, Review, User
from backend.api.auth import get_current_active_user
from backend.agents.base_agent import agent_coordinator

logger = logging.getLogger(__name__)
router = APIRouter()

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

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    is_featured: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = True,
    db: Session = Depends(get_database)
):
    """Get products with filtering and pagination"""
    try:
        query = db.query(Product).filter(Product.is_active == True)
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term)
                )
            )
        
        if is_featured is not None:
            query = query.filter(Product.is_featured == is_featured)
        
        if min_price is not None:
            query = query.filter(Product.current_price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.current_price <= max_price)
        
        if in_stock_only:
            query = query.filter(Product.stock_quantity > 0)
        
        # Order by demand score and featured status
        query = query.order_by(
            Product.is_featured.desc(),
            Product.demand_score.desc(),
            Product.created_at.desc()
        )
        
        products = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for product in products:
            result.append(ProductResponse(
                id=product.id,
                name=product.name,
                description=product.description,
                sku=product.sku,
                category_id=product.category_id,
                category_name=product.category.name if product.category else None,
                base_price=float(product.base_price),
                current_price=float(product.current_price),
                stock_quantity=product.stock_quantity,
                images=product.images or [],
                tags=product.tags or [],
                is_active=product.is_active,
                is_featured=product.is_featured,
                demand_score=product.demand_score,
                price_elasticity=product.price_elasticity
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve products")

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_database)):
    """Get a specific product by ID"""
    try:
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.is_active == True)
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            sku=product.sku,
            category_id=product.category_id,
            category_name=product.category.name if product.category else None,
            base_price=float(product.base_price),
            current_price=float(product.current_price),
            stock_quantity=product.stock_quantity,
            images=product.images or [],
            tags=product.tags or [],
            is_active=product.is_active,
            is_featured=product.is_featured,
            demand_score=product.demand_score,
            price_elasticity=product.price_elasticity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve product")

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Create a new product (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if SKU already exists
        existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="SKU already exists")
        
        # Create new product
        db_product = Product(
            name=product_data.name,
            description=product_data.description,
            sku=product_data.sku,
            category_id=product_data.category_id,
            base_price=product_data.base_price,
            current_price=product_data.current_price,
            cost_price=product_data.cost_price,
            stock_quantity=product_data.stock_quantity,
            min_stock_level=product_data.min_stock_level,
            max_stock_level=product_data.max_stock_level,
            weight=product_data.weight,
            dimensions=product_data.dimensions,
            images=product_data.images,
            tags=product_data.tags,
            is_featured=product_data.is_featured
        )
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        return ProductResponse(
            id=db_product.id,
            name=db_product.name,
            description=db_product.description,
            sku=db_product.sku,
            category_id=db_product.category_id,
            category_name=db_product.category.name if db_product.category else None,
            base_price=float(db_product.base_price),
            current_price=float(db_product.current_price),
            stock_quantity=db_product.stock_quantity,
            images=db_product.images or [],
            tags=db_product.tags or [],
            is_active=db_product.is_active,
            is_featured=db_product.is_featured,
            demand_score=db_product.demand_score,
            price_elasticity=db_product.price_elasticity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create product")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update a product (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            sku=product.sku,
            category_id=product.category_id,
            category_name=product.category.name if product.category else None,
            base_price=float(product.base_price),
            current_price=float(product.current_price),
            stock_quantity=product.stock_quantity,
            images=product.images or [],
            tags=product.tags or [],
            is_active=product.is_active,
            is_featured=product.is_featured,
            demand_score=product.demand_score,
            price_elasticity=product.price_elasticity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update product")

@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_database)):
    """Get all product categories"""
    try:
        categories = db.query(Category).filter(Category.is_active == True).all()
        
        return [
            CategoryResponse(
                id=category.id,
                name=category.name,
                description=category.description,
                is_active=category.is_active
            )
            for category in categories
        ]
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")

@router.get("/{product_id}/recommendations")
async def get_product_recommendations(
    product_id: int,
    limit: int = Query(5, ge=1, le=20),
    current_user: Optional[User] = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get recommendations for a specific product"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get recommendations using the recommendation agent
        if "RecommendationAgent" in agent_coordinator.agents and current_user:
            recommendation_agent = agent_coordinator.agents["RecommendationAgent"]
            recommendations = await recommendation_agent.get_recommendations_for_user(
                current_user.id, limit
            )
            return {"recommendations": recommendations}
        else:
            # Fallback: recommend similar products from same category
            similar_products = db.query(Product).filter(
                and_(
                    Product.category_id == product.category_id,
                    Product.id != product_id,
                    Product.is_active == True,
                    Product.stock_quantity > 0
                )
            ).order_by(Product.demand_score.desc()).limit(limit).all()
            
            recommendations = [
                {
                    "product_id": p.id,
                    "name": p.name,
                    "price": float(p.current_price),
                    "recommendation_score": 0.5
                }
                for p in similar_products
            ]
            
            return {"recommendations": recommendations}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.get("/{product_id}/reviews")
async def get_product_reviews(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_database)
):
    """Get reviews for a specific product"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        reviews = db.query(Review).filter(
            and_(
                Review.product_id == product_id,
                Review.is_approved == True
            )
        ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
        
        # Get review statistics
        review_stats = db.query(
            func.count(Review.id).label('total_reviews'),
            func.avg(Review.rating).label('average_rating'),
            func.sum(Review.helpful_votes).label('total_helpful_votes')
        ).filter(
            and_(
                Review.product_id == product_id,
                Review.is_approved == True
            )
        ).first()
        
        return {
            "reviews": [
                {
                    "id": review.id,
                    "user_id": review.user_id,
                    "rating": review.rating,
                    "title": review.title,
                    "comment": review.comment,
                    "is_verified_purchase": review.is_verified_purchase,
                    "helpful_votes": review.helpful_votes,
                    "created_at": review.created_at.isoformat()
                }
                for review in reviews
            ],
            "statistics": {
                "total_reviews": review_stats.total_reviews or 0,
                "average_rating": round(float(review_stats.average_rating or 0), 1),
                "total_helpful_votes": review_stats.total_helpful_votes or 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to get product reviews")

@router.get("/featured/")
async def get_featured_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_database)
):
    """Get featured products"""
    try:
        products = db.query(Product).filter(
            and_(
                Product.is_featured == True,
                Product.is_active == True,
                Product.stock_quantity > 0
            )
        ).order_by(
            Product.demand_score.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": product.id,
                "name": product.name,
                "current_price": float(product.current_price),
                "images": product.images or [],
                "demand_score": product.demand_score
            }
            for product in products
        ]
        
    except Exception as e:
        logger.error(f"Error getting featured products: {e}")
        raise HTTPException(status_code=500, detail="Failed to get featured products")

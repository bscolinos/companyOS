from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict, Any
import logging
from backend.database.connection import get_database
from backend.database.models import User, CartItem, Product, Review
from backend.api.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    total_price: float
    product_images: List[str]
    stock_available: int

class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    rating: int
    title: Optional[str]
    comment: Optional[str]
    is_verified_purchase: bool
    helpful_votes: int
    created_at: str

@router.get("/cart", response_model=List[CartItemResponse])
async def get_user_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get user's shopping cart"""
    try:
        cart_items = db.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).all()
        
        result = []
        for item in cart_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product and product.is_active:
                result.append(CartItemResponse(
                    id=item.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_price=float(product.current_price),
                    quantity=item.quantity,
                    total_price=float(product.current_price) * item.quantity,
                    product_images=product.images or [],
                    stock_available=product.stock_quantity
                ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting user cart: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cart")

@router.post("/cart", response_model=CartItemResponse)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Add item to shopping cart"""
    try:
        # Verify product exists and is active
        product = db.query(Product).filter(
            and_(Product.id == item_data.product_id, Product.is_active == True)
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock. Available: {product.stock_quantity}"
            )
        
        # Check if item already exists in cart
        existing_item = db.query(CartItem).filter(
            and_(
                CartItem.user_id == current_user.id,
                CartItem.product_id == item_data.product_id
            )
        ).first()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + item_data.quantity
            if product.stock_quantity < new_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: {product.stock_quantity}, Requested: {new_quantity}"
                )
            
            existing_item.quantity = new_quantity
            db.commit()
            db.refresh(existing_item)
            
            return CartItemResponse(
                id=existing_item.id,
                product_id=product.id,
                product_name=product.name,
                product_price=float(product.current_price),
                quantity=existing_item.quantity,
                total_price=float(product.current_price) * existing_item.quantity,
                product_images=product.images or [],
                stock_available=product.stock_quantity
            )
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            
            return CartItemResponse(
                id=cart_item.id,
                product_id=product.id,
                product_name=product.name,
                product_price=float(product.current_price),
                quantity=cart_item.quantity,
                total_price=float(product.current_price) * cart_item.quantity,
                product_images=product.images or [],
                stock_available=product.stock_quantity
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add item to cart")

@router.put("/cart/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update cart item quantity"""
    try:
        cart_item = db.query(CartItem).filter(
            and_(CartItem.id == item_id, CartItem.user_id == current_user.id)
        ).first()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if item_data.quantity <= 0:
            # Remove item if quantity is 0 or negative
            db.delete(cart_item)
            db.commit()
            raise HTTPException(status_code=204, detail="Item removed from cart")
        
        if product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {product.stock_quantity}"
            )
        
        cart_item.quantity = item_data.quantity
        db.commit()
        db.refresh(cart_item)
        
        return CartItemResponse(
            id=cart_item.id,
            product_id=product.id,
            product_name=product.name,
            product_price=float(product.current_price),
            quantity=cart_item.quantity,
            total_price=float(product.current_price) * cart_item.quantity,
            product_images=product.images or [],
            stock_available=product.stock_quantity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cart item: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update cart item")

@router.delete("/cart/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Remove item from cart"""
    try:
        cart_item = db.query(CartItem).filter(
            and_(CartItem.id == item_id, CartItem.user_id == current_user.id)
        ).first()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        db.delete(cart_item)
        db.commit()
        
        return {"message": "Item removed from cart"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing cart item: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove cart item")

@router.delete("/cart")
async def clear_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Clear all items from cart"""
    try:
        db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
        db.commit()
        
        return {"message": "Cart cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to clear cart")

@router.get("/cart/summary")
async def get_cart_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get cart summary with totals"""
    try:
        cart_items = db.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).all()
        
        total_items = 0
        subtotal = 0.0
        
        for item in cart_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product and product.is_active:
                total_items += item.quantity
                subtotal += float(product.current_price) * item.quantity
        
        # Calculate tax and shipping
        tax_amount = subtotal * 0.08  # 8% tax
        shipping_amount = 10.0 if subtotal < 100 else 0.0  # Free shipping over $100
        total_amount = subtotal + tax_amount + shipping_amount
        
        return {
            "total_items": total_items,
            "subtotal": round(subtotal, 2),
            "tax_amount": round(tax_amount, 2),
            "shipping_amount": round(shipping_amount, 2),
            "total_amount": round(total_amount, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting cart summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cart summary")

@router.post("/reviews", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Create a product review"""
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == review_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if user has already reviewed this product
        existing_review = db.query(Review).filter(
            and_(
                Review.user_id == current_user.id,
                Review.product_id == review_data.product_id
            )
        ).first()
        
        if existing_review:
            raise HTTPException(status_code=400, detail="You have already reviewed this product")
        
        # Validate rating
        if not (1 <= review_data.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Create review
        review = Review(
            user_id=current_user.id,
            product_id=review_data.product_id,
            rating=review_data.rating,
            title=review_data.title,
            comment=review_data.comment,
            is_verified_purchase=True  # Would check if user actually purchased the product
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        return ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            product_name=product.name,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            is_verified_purchase=review.is_verified_purchase,
            helpful_votes=review.helpful_votes,
            created_at=review.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create review")

@router.get("/reviews", response_model=List[ReviewResponse])
async def get_user_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get user's reviews"""
    try:
        reviews = db.query(Review).filter(
            Review.user_id == current_user.id
        ).order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
        
        result = []
        for review in reviews:
            product = db.query(Product).filter(Product.id == review.product_id).first()
            if product:
                result.append(ReviewResponse(
                    id=review.id,
                    product_id=review.product_id,
                    product_name=product.name,
                    rating=review.rating,
                    title=review.title,
                    comment=review.comment,
                    is_verified_purchase=review.is_verified_purchase,
                    helpful_votes=review.helpful_votes,
                    created_at=review.created_at.isoformat()
                ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting user reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve reviews")

@router.get("/recommendations")
async def get_user_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user)
):
    """Get personalized recommendations for the user"""
    try:
        # Import here to avoid circular imports
        from backend.agents.base_agent import agent_coordinator
        
        if "RecommendationAgent" in agent_coordinator.agents:
            recommendation_agent = agent_coordinator.agents["RecommendationAgent"]
            recommendations = await recommendation_agent.get_recommendations_for_user(
                current_user.id, limit
            )
            return {"recommendations": recommendations}
        else:
            return {"recommendations": [], "message": "Recommendation service not available"}
        
    except Exception as e:
        logger.error(f"Error getting user recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

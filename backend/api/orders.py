from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import uuid
from backend.database.connection import get_database
from backend.database.models import Order, OrderItem, Product, User, CartItem
from backend.api.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: Dict[str, str]
    billing_address: Optional[Dict[str, str]] = None
    shipping_method: str = "standard"
    payment_method: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: float
    tax_amount: float
    shipping_amount: float
    discount_amount: float
    shipping_address: Dict[str, Any]
    billing_address: Optional[Dict[str, Any]]
    shipping_method: str
    payment_method: str
    payment_status: str
    tracking_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    tracking_number: Optional[str] = None
    payment_status: Optional[str] = None

def calculate_order_totals(items: List[OrderItemCreate], db: Session) -> Dict[str, float]:
    """Calculate order totals"""
    subtotal = 0.0
    
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for product {product.name}"
            )
        
        subtotal += float(product.current_price) * item.quantity
    
    # Simple tax calculation (8% tax rate)
    tax_amount = subtotal * 0.08
    
    # Simple shipping calculation
    shipping_amount = 10.0 if subtotal < 100 else 0.0  # Free shipping over $100
    
    total_amount = subtotal + tax_amount + shipping_amount
    
    return {
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "shipping_amount": shipping_amount,
        "total_amount": total_amount
    }

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Create a new order"""
    try:
        if not order_data.items:
            raise HTTPException(status_code=400, detail="Order must contain at least one item")
        
        # Calculate totals
        totals = calculate_order_totals(order_data.items, db)
        
        # Generate order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        db_order = Order(
            user_id=current_user.id,
            order_number=order_number,
            total_amount=totals["total_amount"],
            tax_amount=totals["tax_amount"],
            shipping_amount=totals["shipping_amount"],
            discount_amount=0.0,
            shipping_address=order_data.shipping_address,
            billing_address=order_data.billing_address or order_data.shipping_address,
            shipping_method=order_data.shipping_method,
            payment_method=order_data.payment_method,
            status="pending",
            payment_status="pending"
        )
        
        db.add(db_order)
        db.flush()  # Get the order ID
        
        # Create order items and update inventory
        order_items = []
        for item_data in order_data.items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            
            # Create order item
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.current_price,
                total_price=float(product.current_price) * item_data.quantity
            )
            
            db.add(order_item)
            order_items.append(order_item)
            
            # Update inventory
            product.stock_quantity -= item_data.quantity
        
        # Clear user's cart
        db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
        
        db.commit()
        db.refresh(db_order)
        
        # Format response
        return OrderResponse(
            id=db_order.id,
            order_number=db_order.order_number,
            status=db_order.status,
            total_amount=float(db_order.total_amount),
            tax_amount=float(db_order.tax_amount),
            shipping_amount=float(db_order.shipping_amount),
            discount_amount=float(db_order.discount_amount),
            shipping_address=db_order.shipping_address,
            billing_address=db_order.billing_address,
            shipping_method=db_order.shipping_method,
            payment_method=db_order.payment_method,
            payment_status=db_order.payment_status,
            tracking_number=db_order.tracking_number,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=float(item.unit_price),
                    total_price=float(item.total_price)
                )
                for item in order_items
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get user's orders"""
    try:
        query = db.query(Order).filter(Order.user_id == current_user.id)
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
        
        result = []
        for order in orders:
            # Get order items
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            
            result.append(OrderResponse(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                total_amount=float(order.total_amount),
                tax_amount=float(order.tax_amount),
                shipping_amount=float(order.shipping_amount),
                discount_amount=float(order.discount_amount),
                shipping_address=order.shipping_address,
                billing_address=order.billing_address,
                shipping_method=order.shipping_method,
                payment_method=order.payment_method,
                payment_status=order.payment_status,
                tracking_number=order.tracking_number,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        product_id=item.product_id,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        unit_price=float(item.unit_price),
                        total_price=float(item.total_price)
                    )
                    for item in items
                ]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting user orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orders")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get a specific order"""
    try:
        order = db.query(Order).filter(
            and_(Order.id == order_id, Order.user_id == current_user.id)
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get order items
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            total_amount=float(order.total_amount),
            tax_amount=float(order.tax_amount),
            shipping_amount=float(order.shipping_amount),
            discount_amount=float(order.discount_amount),
            shipping_address=order.shipping_address,
            billing_address=order.billing_address,
            shipping_method=order.shipping_method,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            tracking_number=order.tracking_number,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=float(item.unit_price),
                    total_price=float(item.total_price)
                )
                for item in items
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve order")

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update order (admin only for most fields, users can cancel)"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check permissions
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Users can only cancel their own pending orders
        if not current_user.is_admin:
            if order_data.status and order_data.status != "cancelled":
                raise HTTPException(status_code=403, detail="Can only cancel orders")
            if order.status not in ["pending", "processing"]:
                raise HTTPException(status_code=400, detail="Cannot cancel order in current status")
        
        # Update fields
        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        order.updated_at = datetime.utcnow()
        
        # If cancelling, restore inventory
        if order_data.status == "cancelled" and order.status != "cancelled":
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            for item in items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
        
        db.commit()
        db.refresh(order)
        
        # Get updated order with items
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            total_amount=float(order.total_amount),
            tax_amount=float(order.tax_amount),
            shipping_amount=float(order.shipping_amount),
            discount_amount=float(order.discount_amount),
            shipping_address=order.shipping_address,
            billing_address=order.billing_address,
            shipping_method=order.shipping_method,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            tracking_number=order.tracking_number,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=float(item.unit_price),
                    total_price=float(item.total_price)
                )
                for item in items
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update order")

@router.get("/admin/all", response_model=List[OrderResponse])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get all orders (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        query = db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
        
        result = []
        for order in orders:
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            
            result.append(OrderResponse(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                total_amount=float(order.total_amount),
                tax_amount=float(order.tax_amount),
                shipping_amount=float(order.shipping_amount),
                discount_amount=float(order.discount_amount),
                shipping_address=order.shipping_address,
                billing_address=order.billing_address,
                shipping_method=order.shipping_method,
                payment_method=order.payment_method,
                payment_status=order.payment_status,
                tracking_number=order.tracking_number,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        product_id=item.product_id,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        unit_price=float(item.unit_price),
                        total_price=float(item.total_price)
                    )
                    for item in items
                ]
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orders")

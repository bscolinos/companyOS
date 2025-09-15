from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

class User(BaseModel):
    id: Optional[int] = None
    email: str
    username: str
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Category(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class Product(BaseModel):
    id: Optional[int] = None
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
    is_active: bool = True
    is_featured: bool = False
    demand_score: float = 0.0
    price_elasticity: float = 1.0
    seasonality_factor: float = 1.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Order(BaseModel):
    id: Optional[int] = None
    user_id: int
    order_number: str
    status: str = "pending"
    total_amount: float
    tax_amount: float = 0.0
    shipping_amount: float = 0.0
    discount_amount: float = 0.0
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: str = "pending"
    payment_id: Optional[str] = None
    risk_score: float = 0.0
    priority_score: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class OrderItem(BaseModel):
    id: Optional[int] = None
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

class CartItem(BaseModel):
    id: Optional[int] = None
    user_id: int
    product_id: int
    quantity: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Review(BaseModel):
    id: Optional[int] = None
    user_id: int
    product_id: int
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    is_verified_purchase: bool = False
    is_approved: bool = True
    sentiment_score: Optional[float] = None
    helpful_votes: int = 0
    created_at: Optional[datetime] = None

class InventoryLog(BaseModel):
    id: Optional[int] = None
    product_id: int
    change_type: str
    quantity_change: int
    previous_quantity: int
    new_quantity: int
    reason: Optional[str] = None
    agent_action: bool = False
    created_at: Optional[datetime] = None

class PriceHistory(BaseModel):
    id: Optional[int] = None
    product_id: int
    old_price: float
    new_price: float
    change_reason: Optional[str] = None
    agent_action: bool = False
    market_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class AgentLog(BaseModel):
    id: Optional[int] = None
    agent_name: str
    action_type: str
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    result: str
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: Optional[datetime] = None

class CustomerInteraction(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    interaction_type: str
    subject: Optional[str] = None
    message: Optional[str] = None
    response: Optional[str] = None
    status: str = "open"
    priority: str = "medium"
    agent_handled: bool = False
    satisfaction_score: Optional[int] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None